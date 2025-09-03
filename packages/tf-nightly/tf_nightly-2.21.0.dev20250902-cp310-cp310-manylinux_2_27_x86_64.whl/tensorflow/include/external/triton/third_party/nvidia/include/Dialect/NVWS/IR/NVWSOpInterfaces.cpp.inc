/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/


/// Get the transaction counts
int mlir::triton::nvws::DescriptorLoadOpInterface::getTxCount() {
      return getImpl()->getTxCount(getImpl(), getOperation());
  }

/// Get the descriptor
::mlir::TypedValue<mlir::triton::TensorDescType> mlir::triton::nvws::DescriptorLoadOpInterface::getDesc() {
      return getImpl()->implDescriptorOpInterface->getDesc(getImpl()->implDescriptorOpInterface, getOperation());
  }
