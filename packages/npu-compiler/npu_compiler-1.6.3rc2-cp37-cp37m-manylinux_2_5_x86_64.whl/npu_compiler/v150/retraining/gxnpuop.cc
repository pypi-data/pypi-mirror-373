#include "tensorflow/core/framework/common_shape_fns.h"
#include "tensorflow/core/framework/op.h"
#include "tensorflow/core/framework/shape_inference.h"
#include "tensorflow/core/util/padding.h"
#include "tensorflow/core/framework/numeric_op.h"
#include "tensorflow/core/framework/tensor.h"
#include "tensorflow/core/lib/core/errors.h"
#include "tensorflow/core/platform/protobuf.h"

using namespace tensorflow;
using shape_inference::InferenceContext;

REGISTER_OP("NPUInference")
	.Input("inputs: inputs_num * float")
	.Input("tf_outputs: outputs_num * float")
	.Attr("inputs_num: int >= 1")
	.Attr("outputs_num: int >= 1")
	.Attr("infer_batch: bool = false")
	.Attr("thread_num: int = 0")
	.Output("outputs: outputs_num * float")
	.SetShapeFn([](InferenceContext* c) {
		int inputs_num, outputs_num;
		c->GetAttr("inputs_num", &inputs_num);
		c->GetAttr("outputs_num", &outputs_num);
		for (int i=0; i<outputs_num; i++) {
			c->set_output(i, c->input(inputs_num+i));
		}
		return Status::OK();
	})
	.Doc(R"doc(
)doc");

// -----------------------------------------------------------------------------

#include<sys/types.h>
#include<sys/socket.h>
#include<unistd.h>
#include<stdlib.h>
#include<errno.h>
#include<arpa/inet.h>
#include<netinet/in.h>
#include<string.h>
#include<pthread.h>

#define ERR_EXIT(m) \
	do { \
		perror(m); \
		exit(EXIT_FAILURE); \
	} while (0)


using tensorflow::DEVICE_CPU;
using tensorflow::OpKernel;
using tensorflow::OpKernelConstruction;
using tensorflow::OpKernelContext;
using tensorflow::Tensor;
using tensorflow::TensorShape;
using tensorflow::TTypes;  // NOLINT This is needed in CUDA mode, do not remove.
using tensorflow::errors::InvalidArgument;

typedef Eigen::ThreadPoolDevice CPUDevice;

static ssize_t socket_send(int conn, const void *buf, size_t size, int flags)
{
	int total_send_size = 0;
	while (total_send_size < size) {
		int send_size = send(conn, buf + total_send_size, size - total_send_size, flags);
		if (send_size == 0) {
			printf("client close\n");
			return -1;
		} else if (send_size == -1) {
			ERR_EXIT("send error");
		}
		total_send_size += send_size;
	}
	return 0;
}

static ssize_t socket_recv(int conn, void *buf, size_t size, int flags)
{
	int total_recv_size = 0;
	while (total_recv_size < size) {
		int recv_size = recv(conn, buf + total_recv_size, size - total_recv_size, flags);
		if (recv_size == 0) {
			printf("client close\n");
			return -1;
		} else if (recv_size == -1) {
			ERR_EXIT("recv error");
		}
		total_recv_size += recv_size;
	}
	return 0;
}

static void update_model(int sock, char *model_buffer, int model_size)
{
	char head[10];
	strcpy(head, "MODEL");

	head[5] = (model_size >> 24) & 0xff;
	head[6] = (model_size >> 16) & 0xff;
	head[7] = (model_size >> 8) & 0xff;
	head[8] = model_size & 0xff;

	socket_send(sock, head, 9, 0);
	socket_send(sock, model_buffer, model_size, 0);
}

static void run_model(int sock, char *src_buffer, int src_size, char *dst_buffer, int dst_size)
{
	char head[6];
	strcpy(head, "INPUT");
	socket_send(sock, head, 5, 0);
	socket_send(sock, src_buffer, src_size, 0);
	socket_recv(sock, dst_buffer, dst_size, 0);
	char end[3];
	strcpy(end, "OK");
	socket_send(sock, end, 2, 0);
#if 0
	printf("result:\n");
	float *fp32_dst_buffer = (float*)dst_buffer;
	for (int i = 0; i < 10; i++) {
		printf("%f, ", fp32_dst_buffer[i]);
	}
	printf("\n");
#endif
}

static int request_socket(void)
{
	int sock;

	if ((sock = socket(PF_INET, SOCK_STREAM, IPPROTO_TCP)) < 0)
		ERR_EXIT("socket error");

	struct sockaddr_in servaddr;
	memset(&servaddr, 0, sizeof(servaddr));
	servaddr.sin_family = AF_INET;
	servaddr.sin_port = htons(5188);
	servaddr.sin_addr.s_addr = inet_addr("127.0.0.1");

	if (connect(sock, (struct sockaddr *)&servaddr, sizeof(servaddr)) < 0)
		ERR_EXIT("connect error");

	return sock;
}

static void close_socket(int sock)
{
	close(sock);
}

static void request_update_model(void)
{
	int sock = request_socket();

	FILE *fp = fopen("model.npu", "r");
	fseek(fp, 0, SEEK_END);
	long model_size = ftell(fp);
	fseek(fp, 0, SEEK_SET);
	char *model_buffer = (char*)malloc(model_size);
	if (model_buffer == NULL) {
		printf("malloc error\n");
		exit(1);
	}
	fread(model_buffer, 1, model_size, fp);
	fclose(fp);

	update_model(sock, model_buffer, model_size);

	free(model_buffer);
	close_socket(sock);
}

static void request_run_model(char *input_buf, int input_total_size, char *output_buf, int output_total_size)
{
	int sock = request_socket();
	run_model(sock, input_buf, input_total_size, output_buf, output_total_size);
	close_socket(sock);
}

static void run_npu(const float **pp_input_data, int *pp_input_num, int input_num,
		float **pp_output_data, int *pp_output_num, int output_num)
{
	int input_total_size, output_total_size;
	input_total_size = 0;
	for (int i=0; i<input_num; i++) {
		input_total_size += pp_input_num[i] * sizeof(float);
	}
	output_total_size = 0;
	for (int i=0; i<output_num; i++) {
		output_total_size += pp_output_num[i] * sizeof(float);
	}

	char *input_buf = (char*)malloc(input_total_size);
	char *output_buf = (char*)malloc(output_total_size);

	if (input_buf == NULL || output_buf == NULL) {
		printf("malloc error\n");
		return;
	}

	int offs = 0;
	for (int i=0; i<input_num; i++) {
		memcpy((void*)(input_buf + offs), (const void*)pp_input_data[i], pp_input_num[i] * sizeof(float));
		offs += pp_input_num[i] * sizeof(float);
	}

	request_run_model(input_buf, input_total_size, output_buf, output_total_size);

	offs = 0;
	for (int i=0; i<output_num; i++) {
		memcpy((void*)pp_output_data[i], (void*)(output_buf + offs), pp_output_num[i] * sizeof(float));
		offs += pp_output_num[i] * sizeof(float);
	}

	free(input_buf);
	free(output_buf);
}

typedef struct _ThreadPara {
	const float **p_input_data;
	int *p_input_num;
	float **p_output_data;
	int *p_output_num;
	int inputs_num;
	int outputs_num;
} ThreadPara;

static void *thread_run_npu(void *arg)
{
	ThreadPara *thread_para = (ThreadPara*)arg;
	run_npu(thread_para->p_input_data, thread_para->p_input_num, thread_para->inputs_num,
			thread_para->p_output_data, thread_para->p_output_num, thread_para->outputs_num);
}

// -----------------------------------------------------------------------------
template <typename Device>
class GxNPUOp : public OpKernel {
public:
	explicit GxNPUOp(OpKernelConstruction* c)
		: OpKernel::OpKernel(c) {
			OP_REQUIRES_OK(c, c->GetAttr("inputs_num", &inputs_num_));
			OP_REQUIRES_OK(c, c->GetAttr("outputs_num", &outputs_num_));
			OP_REQUIRES_OK(c, c->GetAttr("infer_batch", &infer_batch_));
			OP_REQUIRES_OK(c, c->GetAttr("thread_num", &thread_num_));
		}

	void Compute(OpKernelContext* c) override {
		if (infer_batch_)
			_ComputeInferBatch(c);
		else
			_ComputeNormal(c);
	}

	void _ComputeNormal(OpKernelContext* c) {
		const float *p_input_data[MAX_IO_NUM];
		int p_input_num[MAX_IO_NUM];
		float *p_output_data[MAX_IO_NUM];
		int p_output_num[MAX_IO_NUM];

		for (int i=0; i<inputs_num_; i++) {
			const Tensor &input_tensor = c->input(i);
			TensorShape input_shape(input_tensor.shape());
			p_input_data[i] = input_tensor.flat<float>().data();
			p_input_num[i] = 1;
			for (int j=0; j<input_shape.dims(); j++)
				p_input_num[i] *= input_shape.dim_size(j);
		}

		for (int i=0; i<outputs_num_; i++) {
			Tensor *output_tensor = nullptr;
			const Tensor &tf_result = c->input(inputs_num_ + i);
			TensorShape output_shape(tf_result.shape());
			OP_REQUIRES_OK(c, c->allocate_output(i, output_shape, &output_tensor));
			float *output_data = output_tensor->flat<float>().data();
			p_output_data[i] = output_data;
			p_output_num[i] = 1;
			for (int j=0; j<output_shape.dims(); j++)
				p_output_num[i] *= output_shape.dim_size(j);
		}

		request_update_model();
		run_npu(p_input_data, p_input_num, inputs_num_, p_output_data, p_output_num, outputs_num_);
	}

	void _ComputeInferBatch(OpKernelContext* c) {
		const float *p_base_input_data[MAX_IO_NUM];
		float *p_base_output_data[MAX_IO_NUM];
		int p_input_num[MAX_IO_NUM];
		int p_output_num[MAX_IO_NUM];
		const Tensor &input_tensor0 = c->input(0);
		int batch = input_tensor0.shape().dim_size(0);

		for (int i=0; i<inputs_num_; i++) {
			const Tensor &input_tensor = c->input(i);
			TensorShape input_shape(input_tensor.shape());
			p_base_input_data[i] = input_tensor.flat<float>().data();
			p_input_num[i] = 1;
			for (int j=1; j<input_shape.dims(); j++)
				p_input_num[i] *= input_shape.dim_size(j);
		}

		for (int i=0; i<outputs_num_; i++) {
			Tensor *output_tensor = nullptr;
			const Tensor &tf_result = c->input(inputs_num_ + i);
			TensorShape output_shape(tf_result.shape());
			OP_REQUIRES_OK(c, c->allocate_output(i, output_shape, &output_tensor));
			p_base_output_data[i] = output_tensor->flat<float>().data();
			p_output_num[i] = 1;
			for (int j=1; j<output_shape.dims(); j++)
				p_output_num[i] *= output_shape.dim_size(j);
		}

		request_update_model();
		if (thread_num_ == 0) {
			const float *p_input_data[MAX_IO_NUM];
			float *p_output_data[MAX_IO_NUM];
			for (int i=0; i<batch; i++) {
				for (int j=0; j<inputs_num_; j++)
					p_input_data[j] = p_base_input_data[j] + i * p_input_num[j];
				for (int j=0; j<outputs_num_; j++)
					p_output_data[j] = p_base_output_data[j] + i * p_output_num[j];
				run_npu(p_input_data, p_input_num, inputs_num_, p_output_data, p_output_num, outputs_num_);
			}
		} else {
			int loop_num = (batch + thread_num_ - 1) / thread_num_;
			int last_loop_batch_index = (loop_num - 1) * thread_num_;
			int last_loop_batch_num = batch - last_loop_batch_index;
			pthread_t *p_pthread = (pthread_t*)malloc(thread_num_ * sizeof(pthread_t));
			ThreadPara *p_thread_para = (ThreadPara*)malloc(thread_num_ * sizeof(ThreadPara));
			if (p_pthread == NULL || p_thread_para == NULL) {
				printf("malloc error\n");
				return;
			}
			// [thread_num_][MAX_IO_NUM]
			const float **p_input_data = (const float**)malloc(MAX_IO_NUM * thread_num_ * sizeof(float*));
			float **p_output_data = (float**)malloc(MAX_IO_NUM * thread_num_ * sizeof(float*));
			if (p_input_data == NULL || p_output_data == NULL) {
				printf("malloc error\n");
				return;
			}
			for (int i=0; i<loop_num-1; i++) {
				for (int j=0; j<thread_num_; j++) {
					int batch_index = i * thread_num_ + j;
					for (int k=0; k<inputs_num_; k++)
						p_input_data[j*MAX_IO_NUM+k]
							= p_base_input_data[k] + batch_index * p_input_num[k];
					for (int k=0; k<outputs_num_; k++)
						p_output_data[j*MAX_IO_NUM+k]
							= p_base_output_data[k] + batch_index * p_output_num[k];
					p_thread_para[j].p_input_data = &p_input_data[j*MAX_IO_NUM];
					p_thread_para[j].p_input_num = p_input_num;
					p_thread_para[j].p_output_data = &p_output_data[j*MAX_IO_NUM];
					p_thread_para[j].p_output_num = p_output_num;
					p_thread_para[j].inputs_num = inputs_num_;
					p_thread_para[j].outputs_num = outputs_num_;
					pthread_create(&p_pthread[j], NULL, thread_run_npu, (void*)&p_thread_para[j]);
				}
				for (int j=0; j<thread_num_; j++)
					pthread_join(p_pthread[j], NULL);
			}
			// last loop
			for (int j=0; j<last_loop_batch_num; j++) {
				int batch_index = last_loop_batch_index + j;
				for (int k=0; k<inputs_num_; k++)
					p_input_data[j*MAX_IO_NUM+k]
						= p_base_input_data[k] + batch_index * p_input_num[k];
				for (int k=0; k<outputs_num_; k++)
					p_output_data[j*MAX_IO_NUM+k]
						= p_base_output_data[k] + batch_index * p_output_num[k];
				p_thread_para[j].p_input_data = &p_input_data[j*MAX_IO_NUM];
				p_thread_para[j].p_input_num = p_input_num;
				p_thread_para[j].p_output_data = &p_output_data[j*MAX_IO_NUM];
				p_thread_para[j].p_output_num = p_output_num;
				p_thread_para[j].inputs_num = inputs_num_;
				p_thread_para[j].outputs_num = outputs_num_;
				pthread_create(&p_pthread[j], NULL, thread_run_npu, (void*)&p_thread_para[j]);
			}
			for (int j=0; j<last_loop_batch_num; j++)
				pthread_join(p_pthread[j], NULL);
			free(p_pthread);
			free(p_thread_para);
			free(p_input_data);
			free(p_output_data);
		}
	}


private:
	const int MAX_IO_NUM = 10;
	int inputs_num_;
	int outputs_num_;
	bool infer_batch_;
	int thread_num_;
};


REGISTER_KERNEL_BUILDER(Name("NPUInference").Device(DEVICE_CPU), GxNPUOp<CPUDevice>);
