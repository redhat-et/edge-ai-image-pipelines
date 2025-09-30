FROM nvcr.io/nvidia/tensorrt:25.09-py3-igpu
RUN patch -d /workspace/tensorrt/samples -p 1 <<EOF
--- a/Makefile
+++ b/Makefile
@@ -79,6 +79,8 @@ else
   endif
 endif

+samples := sampleOnnxMNIST
+
 .PHONY: all clean help
 all:
        \$(AT)\$(foreach sample, \$(samples), \$(MAKE) -C \$(sample) &&) :
--- a/sampleOnnxMNIST/sampleOnnxMNIST.cpp
+++ b/sampleOnnxMNIST/sampleOnnxMNIST.cpp
@@ -405,6 +405,7 @@ void printHelpInfo()

 int main(int argc, char** argv)
 {
+    sample::setReportableSeverity(ILogger::Severity::kVERBOSE);
     samplesCommon::Args args;
     bool argsOK = samplesCommon::parseArgs(args, argc, argv);
     if (!argsOK)
EOF
RUN make -C /workspace/tensorrt/samples -j 4
WORKDIR /workspace/tensorrt
RUN /workspace/tensorrt/bin/sample_onnx_mnist --useDLACore=0
