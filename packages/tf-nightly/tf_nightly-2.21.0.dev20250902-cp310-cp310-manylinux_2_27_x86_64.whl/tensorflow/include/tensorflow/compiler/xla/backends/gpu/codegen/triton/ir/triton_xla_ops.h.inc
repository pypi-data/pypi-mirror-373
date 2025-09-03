/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Declarations                                                            *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: triton_xla_ops.td                                                    *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace triton {
namespace xla {
/// Extract a tile from a pointer.
/// Offsets, strides, and sizes operands specify the result tensor tile
///     to extract. Shape and minor-to-major layout specify the layout of the source
///     pointer.
/// 
///     Assembly format:
///       from %src as memref<...> [%offsets] [%sizes] [%strides] : tensor_type
/// 
///     Example:
///       ```
///       %extracted_tensor = triton_xla.extract from %src
///         as memref<512x128xbf16, #triton_xla.layout<[1, 0]>>
///         [0, 0] [16, 64] [128, 1] : tensor<16x64xbf16>
///       ```
class ExtractOp;
} // namespace xla
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace xla {
/// Insert a tile into a pointer.
/// Offsets, strides, and source tensor size are used to specify the tile to
///     insert. Shape and minor-to-major layout specify the layout of the
///     destination pointer.
/// 
///     Assembly format:
///       %src into %dst as memref<...> [%offsets] [%sizes] [%strides] : tensor_type
/// 
///     Example:
///       ```
///       triton_xla.insert %src into %dst
///         as memref<512x128xbf16, #triton_xla.layout<[1, 0]>>
///         [0, 0] [8, 8] [1, 1] : tensor<8x8xbf16>
///       ```
class InsertOp;
} // namespace xla
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace xla {
/// Remove a size-1 dimension from a tensor.
class SqueezeDimsOp;
} // namespace xla
} // namespace triton
} // namespace mlir
#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES

namespace mlir {
namespace triton {
namespace xla {

//===----------------------------------------------------------------------===//
// ::mlir::triton::xla::ExtractOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class ExtractOpGenericAdaptorBase {
public:
  struct Properties {
    using src_layoutTy = ::mlir::DenseI64ArrayAttr;
    src_layoutTy src_layout;

    auto getSrcLayout() const {
      auto &propStorage = this->src_layout;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setSrcLayout(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->src_layout = propValue;
    }
    using src_shapeTy = ::mlir::DenseI64ArrayAttr;
    src_shapeTy src_shape;

    auto getSrcShape() const {
      auto &propStorage = this->src_shape;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setSrcShape(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->src_shape = propValue;
    }
    using static_offsetsTy = ::mlir::DenseI64ArrayAttr;
    static_offsetsTy static_offsets;

    auto getStaticOffsets() const {
      auto &propStorage = this->static_offsets;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticOffsets(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_offsets = propValue;
    }
    using static_sizesTy = ::mlir::DenseI64ArrayAttr;
    static_sizesTy static_sizes;

    auto getStaticSizes() const {
      auto &propStorage = this->static_sizes;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticSizes(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_sizes = propValue;
    }
    using static_stridesTy = ::mlir::DenseI64ArrayAttr;
    static_stridesTy static_strides;

    auto getStaticStrides() const {
      auto &propStorage = this->static_strides;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticStrides(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_strides = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 4>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.src_layout == this->src_layout &&
        rhs.src_shape == this->src_shape &&
        rhs.static_offsets == this->static_offsets &&
        rhs.static_sizes == this->static_sizes &&
        rhs.static_strides == this->static_strides &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  ExtractOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("triton_xla.extract", odsAttrs.getContext());
  }

  ExtractOpGenericAdaptorBase(ExtractOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
  ::mlir::DenseI64ArrayAttr getStaticSizesAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_sizes);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticSizes();
  ::mlir::DenseI64ArrayAttr getStaticStridesAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_strides);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticStrides();
  ::mlir::DenseI64ArrayAttr getSrcShapeAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().src_shape);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getSrcShape();
  ::mlir::DenseI64ArrayAttr getSrcLayoutAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().src_layout);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getSrcLayout();
};
} // namespace detail
template <typename RangeT>
class ExtractOpGenericAdaptor : public detail::ExtractOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::ExtractOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_sizes = 2;
  static constexpr int odsIndex_strides = 3;
public:
  ExtractOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  ExtractOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : ExtractOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  ExtractOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : ExtractOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  ExtractOpGenericAdaptor(RangeT values, const ExtractOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = ExtractOp, typename = std::enable_if_t<std::is_same_v<LateInst, ExtractOp>>>
  ExtractOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOffsets() {
    return getODSOperands(1);
  }

  RangeT getSizes() {
    return getODSOperands(2);
  }

  RangeT getStrides() {
    return getODSOperands(3);
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class ExtractOpAdaptor : public ExtractOpGenericAdaptor<::mlir::ValueRange> {
public:
  using ExtractOpGenericAdaptor::ExtractOpGenericAdaptor;
  ExtractOpAdaptor(ExtractOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class ExtractOp : public ::mlir::Op<ExtractOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<1>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OpAsmOpInterface::Trait, ::mlir::OffsetSizeAndStrideOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = ExtractOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = ExtractOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_offsets = 1;
  static constexpr int odsIndex_sizes = 2;
  static constexpr int odsIndex_strides = 3;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("src_layout"), ::llvm::StringRef("src_shape"), ::llvm::StringRef("static_offsets"), ::llvm::StringRef("static_sizes"), ::llvm::StringRef("static_strides"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getSrcLayoutAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getSrcLayoutAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getSrcShapeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getSrcShapeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getStaticOffsetsAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getStaticOffsetsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getStaticSizesAttrName() {
    return getAttributeNameForIndex(3);
  }

  static ::mlir::StringAttr getStaticSizesAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 3);
  }

  ::mlir::StringAttr getStaticStridesAttrName() {
    return getAttributeNameForIndex(4);
  }

  static ::mlir::StringAttr getStaticStridesAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 4);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("triton_xla.extract");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::Operation::operand_range getOffsets() {
    return getODSOperands(1);
  }

  ::mlir::Operation::operand_range getSizes() {
    return getODSOperands(2);
  }

  ::mlir::Operation::operand_range getStrides() {
    return getODSOperands(3);
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getOffsetsMutable();
  ::mlir::MutableOperandRange getSizesMutable();
  ::mlir::MutableOperandRange getStridesMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
  ::mlir::DenseI64ArrayAttr getStaticSizesAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_sizes);
  }

  ::llvm::ArrayRef<int64_t> getStaticSizes();
  ::mlir::DenseI64ArrayAttr getStaticStridesAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_strides);
  }

  ::llvm::ArrayRef<int64_t> getStaticStrides();
  ::mlir::DenseI64ArrayAttr getSrcShapeAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().src_shape);
  }

  ::llvm::ArrayRef<int64_t> getSrcShape();
  ::mlir::DenseI64ArrayAttr getSrcLayoutAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().src_layout);
  }

  ::llvm::ArrayRef<int64_t> getSrcLayout();
  void setStaticOffsetsAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_offsets = attr;
  }

  void setStaticOffsets(::llvm::ArrayRef<int64_t> attrValue);
  void setStaticSizesAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_sizes = attr;
  }

  void setStaticSizes(::llvm::ArrayRef<int64_t> attrValue);
  void setStaticStridesAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_strides = attr;
  }

  void setStaticStrides(::llvm::ArrayRef<int64_t> attrValue);
  void setSrcShapeAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().src_shape = attr;
  }

  void setSrcShape(::llvm::ArrayRef<int64_t> attrValue);
  void setSrcLayoutAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().src_layout = attr;
  }

  void setSrcLayout(::llvm::ArrayRef<int64_t> attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, RankedTensorType result_type, Value src, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, RankedTensorType result_type, Value src, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, RankedTensorType result_type, Value src, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, RankedTensorType result_type, Value src, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, RankedTensorType result_type, Value src, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, RankedTensorType result_type, Value src, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> src_shape, ArrayRef<int64_t> src_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr src_shape, ::mlir::DenseI64ArrayAttr src_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> src_shape, ::llvm::ArrayRef<int64_t> src_layout);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExtractOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static ExtractOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static void getCanonicalizationPatterns(::mlir::RewritePatternSet &results, ::mlir::MLIRContext *context);
  void getAsmResultNames(::mlir::OpAsmSetValueNameFn setNameFn);
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 5 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  SmallVector<Value> getOffsetsAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedOffsets());
  }

  SmallVector<Value> getSizesAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedSizes());
  }

  SmallVector<Value> getStridesAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedStrides());
  }

  /// Return the expected rank of each of the `static_offsets`, `static_sizes`
  /// and `static_strides` attributes.
  std::array<unsigned, 3> getArrayAttrMaxRanks() {
    unsigned rank = getType().getRank();
    return {rank, rank, rank};
  }
  /// Return the number of leading operands before the `offsets`, `sizes` and
  /// and `strides` operands.
  static unsigned getOffsetSizeAndStrideStartOperandIndex() { return 1; }
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::ExtractOp)

namespace mlir {
namespace triton {
namespace xla {

//===----------------------------------------------------------------------===//
// ::mlir::triton::xla::InsertOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class InsertOpGenericAdaptorBase {
public:
  struct Properties {
    using dst_layoutTy = ::mlir::DenseI64ArrayAttr;
    dst_layoutTy dst_layout;

    auto getDstLayout() const {
      auto &propStorage = this->dst_layout;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setDstLayout(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->dst_layout = propValue;
    }
    using dst_shapeTy = ::mlir::DenseI64ArrayAttr;
    dst_shapeTy dst_shape;

    auto getDstShape() const {
      auto &propStorage = this->dst_shape;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setDstShape(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->dst_shape = propValue;
    }
    using static_offsetsTy = ::mlir::DenseI64ArrayAttr;
    static_offsetsTy static_offsets;

    auto getStaticOffsets() const {
      auto &propStorage = this->static_offsets;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticOffsets(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_offsets = propValue;
    }
    using static_sizesTy = ::mlir::DenseI64ArrayAttr;
    static_sizesTy static_sizes;

    auto getStaticSizes() const {
      auto &propStorage = this->static_sizes;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticSizes(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_sizes = propValue;
    }
    using static_stridesTy = ::mlir::DenseI64ArrayAttr;
    static_stridesTy static_strides;

    auto getStaticStrides() const {
      auto &propStorage = this->static_strides;
      return ::llvm::cast<::mlir::DenseI64ArrayAttr>(propStorage);
    }
    void setStaticStrides(const ::mlir::DenseI64ArrayAttr &propValue) {
      this->static_strides = propValue;
    }
    using operandSegmentSizesTy = std::array<int32_t, 5>;
    operandSegmentSizesTy operandSegmentSizes;
    ::llvm::ArrayRef<int32_t> getOperandSegmentSizes() const {
      auto &propStorage = this->operandSegmentSizes;
      return propStorage;
    }
    void setOperandSegmentSizes(::llvm::ArrayRef<int32_t> propValue) {
      auto &propStorage = this->operandSegmentSizes;
      ::llvm::copy(propValue, propStorage.begin());
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.dst_layout == this->dst_layout &&
        rhs.dst_shape == this->dst_shape &&
        rhs.static_offsets == this->static_offsets &&
        rhs.static_sizes == this->static_sizes &&
        rhs.static_strides == this->static_strides &&
        rhs.operandSegmentSizes == this->operandSegmentSizes &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  InsertOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("triton_xla.insert", odsAttrs.getContext());
  }

  InsertOpGenericAdaptorBase(InsertOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
  ::mlir::DenseI64ArrayAttr getStaticSizesAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_sizes);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticSizes();
  ::mlir::DenseI64ArrayAttr getStaticStridesAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_strides);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getStaticStrides();
  ::mlir::DenseI64ArrayAttr getDstShapeAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().dst_shape);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getDstShape();
  ::mlir::DenseI64ArrayAttr getDstLayoutAttr() {
    auto attr = ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().dst_layout);
    return attr;
  }

  ::llvm::ArrayRef<int64_t> getDstLayout();
};
} // namespace detail
template <typename RangeT>
class InsertOpGenericAdaptor : public detail::InsertOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::InsertOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_dst = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_sizes = 3;
  static constexpr int odsIndex_strides = 4;
public:
  InsertOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  InsertOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : InsertOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  InsertOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs) : InsertOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  InsertOpGenericAdaptor(RangeT values, const InsertOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = InsertOp, typename = std::enable_if_t<std::is_same_v<LateInst, InsertOp>>>
  InsertOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  ValueT getDst() {
    return (*getODSOperands(1).begin());
  }

  RangeT getOffsets() {
    return getODSOperands(2);
  }

  RangeT getSizes() {
    return getODSOperands(3);
  }

  RangeT getStrides() {
    return getODSOperands(4);
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class InsertOpAdaptor : public InsertOpGenericAdaptor<::mlir::ValueRange> {
public:
  using InsertOpGenericAdaptor::InsertOpGenericAdaptor;
  InsertOpAdaptor(InsertOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class InsertOp : public ::mlir::Op<InsertOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<2>::Impl, ::mlir::OpTrait::AttrSizedOperandSegments, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::OffsetSizeAndStrideOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = InsertOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = InsertOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  static constexpr int odsIndex_dst = 1;
  static constexpr int odsIndex_offsets = 2;
  static constexpr int odsIndex_sizes = 3;
  static constexpr int odsIndex_strides = 4;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("dst_layout"), ::llvm::StringRef("dst_shape"), ::llvm::StringRef("static_offsets"), ::llvm::StringRef("static_sizes"), ::llvm::StringRef("static_strides"), ::llvm::StringRef("operandSegmentSizes")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getDstLayoutAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getDstLayoutAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getDstShapeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getDstShapeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getStaticOffsetsAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getStaticOffsetsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getStaticSizesAttrName() {
    return getAttributeNameForIndex(3);
  }

  static ::mlir::StringAttr getStaticSizesAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 3);
  }

  ::mlir::StringAttr getStaticStridesAttrName() {
    return getAttributeNameForIndex(4);
  }

  static ::mlir::StringAttr getStaticStridesAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 4);
  }

  ::mlir::StringAttr getOperandSegmentSizesAttrName() {
   return (*this)->getName().getAttributeNames().back();
  }

  static ::mlir::StringAttr getOperandSegmentSizesAttrName(::mlir::OperationName name) {
   return name.getAttributeNames().back();
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("triton_xla.insert");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::triton::PointerType> getDst() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::triton::PointerType>>(*getODSOperands(1).begin());
  }

  ::mlir::Operation::operand_range getOffsets() {
    return getODSOperands(2);
  }

  ::mlir::Operation::operand_range getSizes() {
    return getODSOperands(3);
  }

  ::mlir::Operation::operand_range getStrides() {
    return getODSOperands(4);
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getDstMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getOffsetsMutable();
  ::mlir::MutableOperandRange getSizesMutable();
  ::mlir::MutableOperandRange getStridesMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::DenseI64ArrayAttr getStaticOffsetsAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_offsets);
  }

  ::llvm::ArrayRef<int64_t> getStaticOffsets();
  ::mlir::DenseI64ArrayAttr getStaticSizesAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_sizes);
  }

  ::llvm::ArrayRef<int64_t> getStaticSizes();
  ::mlir::DenseI64ArrayAttr getStaticStridesAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().static_strides);
  }

  ::llvm::ArrayRef<int64_t> getStaticStrides();
  ::mlir::DenseI64ArrayAttr getDstShapeAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().dst_shape);
  }

  ::llvm::ArrayRef<int64_t> getDstShape();
  ::mlir::DenseI64ArrayAttr getDstLayoutAttr() {
    return ::llvm::cast<::mlir::DenseI64ArrayAttr>(getProperties().dst_layout);
  }

  ::llvm::ArrayRef<int64_t> getDstLayout();
  void setStaticOffsetsAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_offsets = attr;
  }

  void setStaticOffsets(::llvm::ArrayRef<int64_t> attrValue);
  void setStaticSizesAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_sizes = attr;
  }

  void setStaticSizes(::llvm::ArrayRef<int64_t> attrValue);
  void setStaticStridesAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().static_strides = attr;
  }

  void setStaticStrides(::llvm::ArrayRef<int64_t> attrValue);
  void setDstShapeAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().dst_shape = attr;
  }

  void setDstShape(::llvm::ArrayRef<int64_t> attrValue);
  void setDstLayoutAttr(::mlir::DenseI64ArrayAttr attr) {
    getProperties().dst_layout = attr;
  }

  void setDstLayout(::llvm::ArrayRef<int64_t> attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, Value src, Value dst, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, Value src, Value dst, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, Value src, Value dst, ValueRange offsets, ValueRange strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, Value src, Value dst, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, Value src, Value dst, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, Value src, Value dst, ArrayRef<OpFoldResult> offsets, ArrayRef<OpFoldResult> strides, ArrayRef<int64_t> dst_shape, ArrayRef<int64_t> dst_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::mlir::DenseI64ArrayAttr static_offsets, ::mlir::DenseI64ArrayAttr static_sizes, ::mlir::DenseI64ArrayAttr static_strides, ::mlir::DenseI64ArrayAttr dst_shape, ::mlir::DenseI64ArrayAttr dst_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::Value dst, ::mlir::ValueRange offsets, ::mlir::ValueRange sizes, ::mlir::ValueRange strides, ::llvm::ArrayRef<int64_t> static_offsets, ::llvm::ArrayRef<int64_t> static_sizes, ::llvm::ArrayRef<int64_t> static_strides, ::llvm::ArrayRef<int64_t> dst_shape, ::llvm::ArrayRef<int64_t> dst_layout);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InsertOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static InsertOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static void getCanonicalizationPatterns(::mlir::RewritePatternSet &results, ::mlir::MLIRContext *context);
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 5 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  SmallVector<Value> getOffsetsAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedOffsets());
  }

  SmallVector<Value> getSizesAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedSizes());
  }

  SmallVector<Value> getStridesAsValues(::mlir::ImplicitLocOpBuilder &b) {
    return ::mlir::getValueOrCreateConstantIndexOp(b, b.getLoc(),
      getMixedStrides());
  }

  /// Return the expected rank of each of the `static_offsets`, `static_sizes`
  /// and `static_strides` attributes.
  std::array<unsigned, 3> getArrayAttrMaxRanks() {
    unsigned rank = getSrc().getType().getRank();
    return {rank, rank, rank};
  }
  /// Return the number of leading operands before the `offsets`, `sizes` and
  /// and `strides` operands.
  static unsigned getOffsetSizeAndStrideStartOperandIndex() { return 2; }
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::InsertOp)

namespace mlir {
namespace triton {
namespace xla {

//===----------------------------------------------------------------------===//
// ::mlir::triton::xla::SqueezeDimsOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class SqueezeDimsOpGenericAdaptorBase {
public:
  struct Properties {
    using axisTy = ::mlir::IntegerAttr;
    axisTy axis;

    auto getAxis() const {
      auto &propStorage = this->axis;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setAxis(const ::mlir::IntegerAttr &propValue) {
      this->axis = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.axis == this->axis &&
        true;
    }
    bool operator!=(const Properties &rhs) const {
      return !(*this == rhs);
    }
  };
protected:
  ::mlir::DictionaryAttr odsAttrs;
  ::std::optional<::mlir::OperationName> odsOpName;
  Properties properties;
  ::mlir::RegionRange odsRegions;
public:
  SqueezeDimsOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("triton_xla.squeeze_dims", odsAttrs.getContext());
  }

  SqueezeDimsOpGenericAdaptorBase(SqueezeDimsOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::IntegerAttr getAxisAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().axis);
    return attr;
  }

  uint32_t getAxis();
};
} // namespace detail
template <typename RangeT>
class SqueezeDimsOpGenericAdaptor : public detail::SqueezeDimsOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::SqueezeDimsOpGenericAdaptorBase;
  static constexpr int odsIndex_src = 0;
public:
  SqueezeDimsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  SqueezeDimsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : SqueezeDimsOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  SqueezeDimsOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : SqueezeDimsOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  SqueezeDimsOpGenericAdaptor(RangeT values, const SqueezeDimsOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = SqueezeDimsOp, typename = std::enable_if_t<std::is_same_v<LateInst, SqueezeDimsOp>>>
  SqueezeDimsOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getSrc() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class SqueezeDimsOpAdaptor : public SqueezeDimsOpGenericAdaptor<::mlir::ValueRange> {
public:
  using SqueezeDimsOpGenericAdaptor::SqueezeDimsOpGenericAdaptor;
  SqueezeDimsOpAdaptor(SqueezeDimsOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class SqueezeDimsOp : public ::mlir::Op<SqueezeDimsOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::RankedTensorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::ConditionallySpeculatable::Trait, ::mlir::OpTrait::AlwaysSpeculatableImplTrait, ::mlir::MemoryEffectOpInterface::Trait, ::mlir::OpTrait::SameOperandsAndResultElementType> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = SqueezeDimsOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = SqueezeDimsOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_src = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("axis")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getAxisAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getAxisAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("triton_xla.squeeze_dims");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getSrc() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getSrcMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::RankedTensorType> getResult() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::RankedTensorType>>(*getODSResults(0).begin());
  }

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::IntegerAttr getAxisAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().axis);
  }

  uint32_t getAxis();
  void setAxisAttr(::mlir::IntegerAttr attr) {
    getProperties().axis = attr;
  }

  void setAxis(uint32_t attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, ::mlir::IntegerAttr axis);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type result, ::mlir::Value src, uint32_t axis);
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type result, ::mlir::Value src, uint32_t axis);
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type result, ::mlir::Value src, uint32_t axis);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value src, uint32_t axis);
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value src, uint32_t axis);
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value src, uint32_t axis);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static SqueezeDimsOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static SqueezeDimsOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 1 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace xla
} // namespace triton
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::triton::xla::SqueezeDimsOp)


#endif  // GET_OP_CLASSES

