/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* AttrDef Declarations                                                       *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

#ifdef GET_ATTRDEF_CLASSES
#undef GET_ATTRDEF_CLASSES


namespace mlir {
class AsmParser;
class AsmPrinter;
} // namespace mlir
namespace mlir {
namespace triton {
namespace xla {
/// tensor map swizzle mode
class SwizzleModeAttr;
/// Contains the necessary data to generate TMA descriptors.
class TmaDescriptorAttr;
class LayoutAttr;
namespace detail {
struct SwizzleModeAttrStorage;
} // namespace detail
class SwizzleModeAttr : public ::mlir::Attribute::AttrBase<SwizzleModeAttr, ::mlir::Attribute, detail::SwizzleModeAttrStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "triton_xla.swizzle_mode";
  static constexpr ::llvm::StringLiteral dialectName = "triton_xla";
  static SwizzleModeAttr get(::mlir::MLIRContext *context, ::mlir::triton::xla::SwizzleMode value);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"swizzle_mode"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::mlir::triton::xla::SwizzleMode getValue() const;
};
namespace detail {
struct TmaDescriptorAttrStorage;
} // namespace detail
class TmaDescriptorAttr : public ::mlir::Attribute::AttrBase<TmaDescriptorAttr, ::mlir::Attribute, detail::TmaDescriptorAttrStorage> {
public:
  using Base::Base;
  static constexpr ::llvm::StringLiteral name = "triton_xla.tma_descriptor";
  static constexpr ::llvm::StringLiteral dialectName = "triton_xla";
  static TmaDescriptorAttr get(::mlir::MLIRContext *context, ::llvm::ArrayRef<int64_t> global_shape, ::llvm::ArrayRef<int64_t> tile_shape, ::llvm::ArrayRef<int64_t> tile_strides, ::llvm::ArrayRef<int64_t> layout, int element_byte_size, SwizzleModeAttr swizzle_mode);
  static TmaDescriptorAttr get(::mlir::MLIRContext *context, ArrayRef<int64_t> global_shape, ArrayRef<int64_t> tile_shape, ArrayRef<int64_t> tile_strides, ArrayRef<int64_t> layout, int element_byte_size);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"tma_descriptor"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::llvm::ArrayRef<int64_t> getGlobalShape() const;
  ::llvm::ArrayRef<int64_t> getTileShape() const;
  ::llvm::ArrayRef<int64_t> getTileStrides() const;
  ::llvm::ArrayRef<int64_t> getLayout() const;
  int getElementByteSize() const;
  SwizzleModeAttr getSwizzleMode() const;
};
namespace detail {
struct LayoutAttrStorage;
} // namespace detail
class LayoutAttr : public ::mlir::Attribute::AttrBase<LayoutAttr, ::mlir::Attribute, detail::LayoutAttrStorage, ::mlir::MemRefLayoutAttrInterface::Trait> {
public:
  using Base::Base;
  LogicalResult verifyLayout(
      ArrayRef<int64_t> shape, function_ref<InFlightDiagnostic()> emit_error) const;
  LogicalResult getStridesAndOffset(
      ArrayRef<int64_t> shape, SmallVectorImpl<int64_t>& strides, int64_t& offset) const;
  static constexpr ::llvm::StringLiteral name = "triton_xla.layout";
  static constexpr ::llvm::StringLiteral dialectName = "triton_xla";
  static LayoutAttr get(::mlir::MLIRContext *context, ::mlir::DenseI64ArrayAttr minor_to_major);
  static constexpr ::llvm::StringLiteral getMnemonic() {
    return {"layout"};
  }

  static ::mlir::Attribute parse(::mlir::AsmParser &odsParser, ::mlir::Type odsType);
  void print(::mlir::AsmPrinter &odsPrinter) const;
  ::mlir::DenseI64ArrayAttr getMinorToMajor() const;
  ::mlir::AffineMap getAffineMap() const;
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::SwizzleModeAttr)
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::TmaDescriptorAttr)
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::LayoutAttr)

#endif  // GET_ATTRDEF_CLASSES

