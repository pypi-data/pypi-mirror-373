/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Enum Utility Definitions                                                   *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: TritonInstrumentOps.td                                               *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace triton {
namespace instrument {
::llvm::StringRef stringifyMemType(MemType val) {
  switch (val) {
    case MemType::SHARED: return "shared";
    case MemType::TENSOR: return "tensor";
  }
  return "";
}

::std::optional<MemType> symbolizeMemType(::llvm::StringRef str) {
  return ::llvm::StringSwitch<::std::optional<MemType>>(str)
      .Case("shared", MemType::SHARED)
      .Case("tensor", MemType::TENSOR)
      .Default(::std::nullopt);
}
::std::optional<MemType> symbolizeMemType(uint32_t value) {
  switch (value) {
  case 0: return MemType::SHARED;
  case 1: return MemType::TENSOR;
  default: return ::std::nullopt;
  }
}

bool MemTypeAttr::classof(::mlir::Attribute attr) {
  return (((::llvm::isa<::mlir::IntegerAttr>(attr))) && ((::llvm::cast<::mlir::IntegerAttr>(attr).getType().isSignlessInteger(32)))) && (((
    ::llvm::cast<::mlir::IntegerAttr>(attr).getValue().eq(::llvm::APInt(32, 0)))) || ((
    ::llvm::cast<::mlir::IntegerAttr>(attr).getValue().eq(::llvm::APInt(32, 1)))));
}
MemTypeAttr MemTypeAttr::get(::mlir::MLIRContext *context, MemType val) {
  ::mlir::IntegerType intType = ::mlir::IntegerType::get(context, 32);
  ::mlir::IntegerAttr baseAttr = ::mlir::IntegerAttr::get(intType, static_cast<uint32_t>(val));
  return ::llvm::cast<MemTypeAttr>(baseAttr);
}
MemType MemTypeAttr::getValue() const {
  return static_cast<MemType>(::mlir::IntegerAttr::getValue().getZExtValue());
}
} // namespace instrument
} // namespace triton
} // namespace mlir

