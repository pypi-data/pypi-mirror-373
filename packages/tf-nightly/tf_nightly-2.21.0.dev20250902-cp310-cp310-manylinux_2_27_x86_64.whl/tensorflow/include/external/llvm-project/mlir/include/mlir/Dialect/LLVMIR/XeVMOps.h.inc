/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Op Declarations                                                            *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|* From: XeVMOps.td                                                           *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace xevm {
/// 2D block load
/// The `xevm.blockload2d` operation loads a two dimensional matrix tile
///     from a base matrix residing in global memory. The parameters are:
///       * `ptr` - the base address of the base matrix containing the tile to load
///       * `base_width` - the width of the base matrix in number of bytes.
///       * `base_height` - the number of rows in the base matrix
///       * `base_pitch` - the physical stride between the first columns of the current
///         row and the subsequent row in number of bytes.
///       * `x`, `y`, `tile_width`, `tile_height` - the starting offsets and shape of
///         the tile to load in number of elements.
///       * `elem_size_in_bits` - the size in bits of the matrix element type
///         - 32 for f32, tf32
///         - 16 for f16, int16, bf16
///         - 8 for int8
///       * `v_blocks` - number of consecutive tiles in innermost dimension direction to load
///       * `transpose` - transpose the tile in registers (useful for 32 bit element type)
///       * `pack_register` - pack element types narrower than register bit width.
///         [M, N] => [M/factor, N, factor] where factor is register_size_in_bits / elem_size_in_bits
///       * `cache_control` - an enumerator that sets the cache behaviour
/// 
///     Notes:
///       - the `transpose` and `pack_register` parameters are mutual exclusive
///       - transposing the tile loaded is used for A matrix in backward path or used for the B matrix operand
///         (D = C + A * B), where A has row-major layout and B should have column-major layout in memory.
///       - if the tile loaded contains out of bound elements of the matrix, they are filled with 0.
/// 
///     Example:
///     ```mlir
///       %base_width_a = arith.constant 32 : i32
///       %base_height_a = arith.constant 8 : i32
///       %base_pitch_a = arith.constant 32 : i32
///       %x = arith.constant 0 : i32
///       %y = arith.constant 0 : i32
///       %loaded_a = xevm.blockload2d %src, %base_width_a, %base_height_a, %base_pitch_a, %x, %y
///                     <{elem_size_in_bits=16 : i32, tile_width=16 : i32, tile_height=8 : i32,
///                       v_blocks=1 : i32, transpose=false : i32, pack_register=false,
///                       cache_control=#xevm.load_cache_control<Default>}>
///                     : (!llvm.ptr<1>, i32, i32, i32, i32, i32) -> vector<8xi16>
///     ```
class BlockLoad2dOp;
} // namespace xevm
} // namespace mlir
namespace mlir {
namespace xevm {
/// 2D block prefetch
/// The `xevm.blockprefetch2d` operation prefetches a two dimensional tile
///     from a larger base matrix residing in global memory. The parameters are:
///       * `ptr` - the base address of the base matrix containing the tile to prefetch
///       * `base_width` - the width of the base matrix in number of bytes.
///       * `base_height` - the number of rows in the base matrix
///       * `base_pitch` - the physical stride between the first columns of the current
///         row and the subsequent row in number of bytes.
///       * `x`, `y`, `tile_width`, `tile_height` - the starting offsets and shape of tile
///         to prefetch in number of elements.
///       * `elem_size_in_bits` - the size in bits of the matrix element
///         - 32 for f32, bf32
///         - 16 for f16, int16, bf16
///         - 8 for int8, int4, int2
///       * `v_blocks` - number of tiles in innermost dimension direction to prefetch
///       * `cache_control` - an enumerator that sets the cache behaviour
/// 
///     Example:
///     ```mlir
///       xevm.blockprefetch2d %ptr, %base_width, %base_height, %base_pitch, %x, %y
///         <{elem_size_in_bits=8 : i32, tile_width=32 : i32, tile_height=8 : i32,
///           v_blocks=1 : i32, cache_control=#xevm.load_cache_control<L1uc_L2uc_L3uc>}>
///         : (!llvm.ptr<1>, i32, i32, i32, i32, i32)
///     ```
class BlockPrefetch2dOp;
} // namespace xevm
} // namespace mlir
namespace mlir {
namespace xevm {
/// 2D block store
/// The `xevm.blockstore2d` operation stores a two dimensional tile into a
///     larger matrix residing in global memory. The parameters are:
///       * `ptr` - the base address of the target matrix where to store the tile
///       * `base_width` - the width of the base matrix in number of bytes.
///       * `base_height` - the number of rows in the base matrix
///       * `base_pitch` - the physical stride between the first columns of the current
///         row and the subsequent row in number of bytes.
///       * `x`, `y`, `tile_width`, `tile_height` - the starting offsets and shape of the tile to store
///       in number of elements.
///       * `elem_size_in_bits` - the size in bits of the matrix element
///         - 32 for f32, tf32
///         - 16 for f16, int16, bf16
///         - 8 for int8
///       * `cache_control` - an enumerator that sets the cache behaviour
///       * `stored_val` - the tile to store
/// 
///     Example:
///     ```mlir
///       %base_width_c = arith.constant 64 : i32
///       %base_height_c = arith.constant 8 : i32
///       %base_pitch_c = arith.constant 64 : i32
///       %x = arith.constant 0 : i32
///       %y = arith.constant 0 : i32
///       xevm.blockstore2d %dst, %base_width_c, %base_height_c, %base_pitch_c, %x, %y, %src
///         <{elem_size_in_bits=32 : i32, tile_width=16 : i32, tile_height=8 : i32,
///           cache_control=#xevm.load_cache_control<Default>}>
///         : (!llvm.ptr<1>, i32, i32, i32, i32, i32, vector<8xi32>)
///     ```
class BlockStore2dOp;
} // namespace xevm
} // namespace mlir
namespace mlir {
namespace xevm {
/// Subgroup matrix multiply-add
/// The `xevm.mma` is a cooperative operation where all threads/lanes in
///     a subgroup participates and carries out matrix multiplication plus accumulation:
/// 
///       D = C + A x B
/// 
///       where the A, B, C input matrices and the result D have shapes:
///         - D : MxN
///         - C : MxN
///         - A : MxK
///         - B : KxN
/// 
///     Parameters:
///       * `a` - vector of matrix A elements.
///       * `b` - vector of matrix B elements.
///       * `c` - (optional) vector of matrix C elements.
///       * `shape` - the shape of the matrices, specified as `M`, `N`, and `K` values.
///       * `types` - the data types of the matrices, specified as `D`, `A`, `B`, and optionally `C`.
/// 
///     Example:
///     ```mlir
///       %d = xevm.mma %a, %b, %c { shape=<m=8, n=16, k=16>, types=<d=f32, a=f16, b=f16, c=f32> }
///              : (vector<8xi16>, vector<8xi32>, vector<8xf32>) -> vector<8xf32>
///     ```
class MMAOp;
} // namespace xevm
} // namespace mlir
namespace mlir {
namespace xevm {
/// Work-item's memory fence.
/// This operation ensures that all prior memory accesses of this
///     work-item to `addrspace` are visible to all other work-items in `scope`.
///     Parameters description:
///       * `scope` - specify the memory scope at which all other work-items should observe
///         memory operations prior to the fence.
///       * `addrspace` - specify the address space of work-item's memory accesses
///         to be affected by the fence.
class MemfenceOp;
} // namespace xevm
} // namespace mlir
namespace mlir {
namespace xevm {
/// Prefetch data into a cache subsystem.
/// Work-item issues a prefetch from global memory to cache:
///       * `ptr` - LLVM pointer with address space. Address space must be 1 (global)
///         or 4 (generic)
///       * `cache_control` - specify caching options
class PrefetchOp;
} // namespace xevm
} // namespace mlir
#ifdef GET_OP_CLASSES
#undef GET_OP_CLASSES

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::BlockLoad2dOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BlockLoad2dOpGenericAdaptorBase {
public:
  struct Properties {
    using cache_controlTy = ::mlir::xevm::LoadCacheControlAttr;
    cache_controlTy cache_control;

    auto getCacheControl() const {
      auto &propStorage = this->cache_control;
      return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(propStorage);
    }
    void setCacheControl(const ::mlir::xevm::LoadCacheControlAttr &propValue) {
      this->cache_control = propValue;
    }
    using elem_size_in_bitsTy = ::mlir::IntegerAttr;
    elem_size_in_bitsTy elem_size_in_bits;

    auto getElemSizeInBits() const {
      auto &propStorage = this->elem_size_in_bits;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setElemSizeInBits(const ::mlir::IntegerAttr &propValue) {
      this->elem_size_in_bits = propValue;
    }
    using pack_registerTy = ::mlir::IntegerAttr;
    pack_registerTy pack_register;

    auto getPackRegister() const {
      auto &propStorage = this->pack_register;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setPackRegister(const ::mlir::IntegerAttr &propValue) {
      this->pack_register = propValue;
    }
    using tile_heightTy = ::mlir::IntegerAttr;
    tile_heightTy tile_height;

    auto getTileHeight() const {
      auto &propStorage = this->tile_height;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileHeight(const ::mlir::IntegerAttr &propValue) {
      this->tile_height = propValue;
    }
    using tile_widthTy = ::mlir::IntegerAttr;
    tile_widthTy tile_width;

    auto getTileWidth() const {
      auto &propStorage = this->tile_width;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileWidth(const ::mlir::IntegerAttr &propValue) {
      this->tile_width = propValue;
    }
    using transposeTy = ::mlir::IntegerAttr;
    transposeTy transpose;

    auto getTranspose() const {
      auto &propStorage = this->transpose;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTranspose(const ::mlir::IntegerAttr &propValue) {
      this->transpose = propValue;
    }
    using v_blocksTy = ::mlir::IntegerAttr;
    v_blocksTy v_blocks;

    auto getVBlocks() const {
      auto &propStorage = this->v_blocks;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setVBlocks(const ::mlir::IntegerAttr &propValue) {
      this->v_blocks = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache_control == this->cache_control &&
        rhs.elem_size_in_bits == this->elem_size_in_bits &&
        rhs.pack_register == this->pack_register &&
        rhs.tile_height == this->tile_height &&
        rhs.tile_width == this->tile_width &&
        rhs.transpose == this->transpose &&
        rhs.v_blocks == this->v_blocks &&
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
  BlockLoad2dOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.blockload2d", odsAttrs.getContext());
  }

  BlockLoad2dOpGenericAdaptorBase(BlockLoad2dOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
    return attr;
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
    return attr;
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
    return attr;
  }

  uint32_t getTileHeight();
  ::mlir::IntegerAttr getVBlocksAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().v_blocks);
    return attr;
  }

  uint32_t getVBlocks();
  ::mlir::IntegerAttr getTransposeAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().transpose);
    return attr;
  }

  bool getTranspose();
  ::mlir::IntegerAttr getPackRegisterAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().pack_register);
    return attr;
  }

  bool getPackRegister();
  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    auto attr = ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
    return attr;
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
};
} // namespace detail
template <typename RangeT>
class BlockLoad2dOpGenericAdaptor : public detail::BlockLoad2dOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BlockLoad2dOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
public:
  BlockLoad2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BlockLoad2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BlockLoad2dOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BlockLoad2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : BlockLoad2dOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BlockLoad2dOpGenericAdaptor(RangeT values, const BlockLoad2dOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BlockLoad2dOp, typename = std::enable_if_t<std::is_same_v<LateInst, BlockLoad2dOp>>>
  BlockLoad2dOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBaseWidth() {
    return (*getODSOperands(1).begin());
  }

  ValueT getBaseHeight() {
    return (*getODSOperands(2).begin());
  }

  ValueT getBasePitch() {
    return (*getODSOperands(3).begin());
  }

  ValueT getX() {
    return (*getODSOperands(4).begin());
  }

  ValueT getY() {
    return (*getODSOperands(5).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BlockLoad2dOpAdaptor : public BlockLoad2dOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BlockLoad2dOpGenericAdaptor::BlockLoad2dOpGenericAdaptor;
  BlockLoad2dOpAdaptor(BlockLoad2dOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BlockLoad2dOp : public ::mlir::Op<BlockLoad2dOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::VectorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<6>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BlockLoad2dOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BlockLoad2dOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache_control"), ::llvm::StringRef("elem_size_in_bits"), ::llvm::StringRef("pack_register"), ::llvm::StringRef("tile_height"), ::llvm::StringRef("tile_width"), ::llvm::StringRef("transpose"), ::llvm::StringRef("v_blocks")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheControlAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheControlAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getElemSizeInBitsAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getElemSizeInBitsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getPackRegisterAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getPackRegisterAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getTileHeightAttrName() {
    return getAttributeNameForIndex(3);
  }

  static ::mlir::StringAttr getTileHeightAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 3);
  }

  ::mlir::StringAttr getTileWidthAttrName() {
    return getAttributeNameForIndex(4);
  }

  static ::mlir::StringAttr getTileWidthAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 4);
  }

  ::mlir::StringAttr getTransposeAttrName() {
    return getAttributeNameForIndex(5);
  }

  static ::mlir::StringAttr getTransposeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 5);
  }

  ::mlir::StringAttr getVBlocksAttrName() {
    return getAttributeNameForIndex(6);
  }

  static ::mlir::StringAttr getVBlocksAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 6);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.blockload2d");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::LLVM::LLVMPointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::LLVM::LLVMPointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseWidth() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseHeight() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBasePitch() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getX() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(4).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getY() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(5).begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseWidthMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseHeightMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBasePitchMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getXMutable() {
    auto range = getODSOperandIndexAndLength(4);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getYMutable() {
    auto range = getODSOperandIndexAndLength(5);
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

  ::mlir::TypedValue<::mlir::VectorType> getRes() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*getODSResults(0).begin());
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
  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
  }

  uint32_t getTileHeight();
  ::mlir::IntegerAttr getVBlocksAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().v_blocks);
  }

  uint32_t getVBlocks();
  ::mlir::IntegerAttr getTransposeAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().transpose);
  }

  bool getTranspose();
  ::mlir::IntegerAttr getPackRegisterAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().pack_register);
  }

  bool getPackRegister();
  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
  void setElemSizeInBitsAttr(::mlir::IntegerAttr attr) {
    getProperties().elem_size_in_bits = attr;
  }

  void setElemSizeInBits(uint32_t attrValue);
  void setTileWidthAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_width = attr;
  }

  void setTileWidth(uint32_t attrValue);
  void setTileHeightAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_height = attr;
  }

  void setTileHeight(uint32_t attrValue);
  void setVBlocksAttr(::mlir::IntegerAttr attr) {
    getProperties().v_blocks = attr;
  }

  void setVBlocks(uint32_t attrValue);
  void setTransposeAttr(::mlir::IntegerAttr attr) {
    getProperties().transpose = attr;
  }

  void setTranspose(bool attrValue);
  void setPackRegisterAttr(::mlir::IntegerAttr attr) {
    getProperties().pack_register = attr;
  }

  void setPackRegister(bool attrValue);
  void setCacheControlAttr(::mlir::xevm::LoadCacheControlAttr attr) {
    getProperties().cache_control = attr;
  }

  void setCacheControl(::std::optional<::mlir::xevm::LoadCacheControl> attrValue);
  ::mlir::Attribute removeCacheControlAttr() {
      auto attr = getProperties().cache_control;
      getProperties().cache_control = {};
      return attr;
  }

  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, ::mlir::IntegerAttr transpose, ::mlir::IntegerAttr pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type res, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, bool transpose, bool pack_register, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockLoad2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockLoad2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  static ::llvm::LogicalResult setPropertiesFromParsedAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 7 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  void printProperties(::mlir::MLIRContext *ctx,
          ::mlir::OpAsmPrinter &p, const Properties &prop,
          ::mlir::ArrayRef<::llvm::StringRef> elidedProps) {
    Attribute propAttr = getPropertiesAsAttr(ctx, prop);
    if (propAttr)
      p << "<" << propAttr << ">";
  }

  static ::mlir::ParseResult parseProperties(::mlir::OpAsmParser &parser,
                                   ::mlir::OperationState &result) {
    if (mlir::succeeded(parser.parseOptionalLess())) {
      if (parser.parseAttribute(result.propertiesAttr) || parser.parseGreater())
        return failure();
    }
    return success();
  }


};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::BlockLoad2dOp)

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::BlockPrefetch2dOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BlockPrefetch2dOpGenericAdaptorBase {
public:
  struct Properties {
    using cache_controlTy = ::mlir::xevm::LoadCacheControlAttr;
    cache_controlTy cache_control;

    auto getCacheControl() const {
      auto &propStorage = this->cache_control;
      return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(propStorage);
    }
    void setCacheControl(const ::mlir::xevm::LoadCacheControlAttr &propValue) {
      this->cache_control = propValue;
    }
    using elem_size_in_bitsTy = ::mlir::IntegerAttr;
    elem_size_in_bitsTy elem_size_in_bits;

    auto getElemSizeInBits() const {
      auto &propStorage = this->elem_size_in_bits;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setElemSizeInBits(const ::mlir::IntegerAttr &propValue) {
      this->elem_size_in_bits = propValue;
    }
    using tile_heightTy = ::mlir::IntegerAttr;
    tile_heightTy tile_height;

    auto getTileHeight() const {
      auto &propStorage = this->tile_height;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileHeight(const ::mlir::IntegerAttr &propValue) {
      this->tile_height = propValue;
    }
    using tile_widthTy = ::mlir::IntegerAttr;
    tile_widthTy tile_width;

    auto getTileWidth() const {
      auto &propStorage = this->tile_width;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileWidth(const ::mlir::IntegerAttr &propValue) {
      this->tile_width = propValue;
    }
    using v_blocksTy = ::mlir::IntegerAttr;
    v_blocksTy v_blocks;

    auto getVBlocks() const {
      auto &propStorage = this->v_blocks;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setVBlocks(const ::mlir::IntegerAttr &propValue) {
      this->v_blocks = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache_control == this->cache_control &&
        rhs.elem_size_in_bits == this->elem_size_in_bits &&
        rhs.tile_height == this->tile_height &&
        rhs.tile_width == this->tile_width &&
        rhs.v_blocks == this->v_blocks &&
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
  BlockPrefetch2dOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.blockprefetch2d", odsAttrs.getContext());
  }

  BlockPrefetch2dOpGenericAdaptorBase(BlockPrefetch2dOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
    return attr;
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
    return attr;
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
    return attr;
  }

  uint32_t getTileHeight();
  ::mlir::IntegerAttr getVBlocksAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().v_blocks);
    return attr;
  }

  uint32_t getVBlocks();
  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    auto attr = ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
    return attr;
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
};
} // namespace detail
template <typename RangeT>
class BlockPrefetch2dOpGenericAdaptor : public detail::BlockPrefetch2dOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BlockPrefetch2dOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
public:
  BlockPrefetch2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BlockPrefetch2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BlockPrefetch2dOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BlockPrefetch2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : BlockPrefetch2dOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BlockPrefetch2dOpGenericAdaptor(RangeT values, const BlockPrefetch2dOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BlockPrefetch2dOp, typename = std::enable_if_t<std::is_same_v<LateInst, BlockPrefetch2dOp>>>
  BlockPrefetch2dOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBaseWidth() {
    return (*getODSOperands(1).begin());
  }

  ValueT getBaseHeight() {
    return (*getODSOperands(2).begin());
  }

  ValueT getBasePitch() {
    return (*getODSOperands(3).begin());
  }

  ValueT getX() {
    return (*getODSOperands(4).begin());
  }

  ValueT getY() {
    return (*getODSOperands(5).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BlockPrefetch2dOpAdaptor : public BlockPrefetch2dOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BlockPrefetch2dOpGenericAdaptor::BlockPrefetch2dOpGenericAdaptor;
  BlockPrefetch2dOpAdaptor(BlockPrefetch2dOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BlockPrefetch2dOp : public ::mlir::Op<BlockPrefetch2dOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<6>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BlockPrefetch2dOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BlockPrefetch2dOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache_control"), ::llvm::StringRef("elem_size_in_bits"), ::llvm::StringRef("tile_height"), ::llvm::StringRef("tile_width"), ::llvm::StringRef("v_blocks")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheControlAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheControlAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getElemSizeInBitsAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getElemSizeInBitsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getTileHeightAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getTileHeightAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getTileWidthAttrName() {
    return getAttributeNameForIndex(3);
  }

  static ::mlir::StringAttr getTileWidthAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 3);
  }

  ::mlir::StringAttr getVBlocksAttrName() {
    return getAttributeNameForIndex(4);
  }

  static ::mlir::StringAttr getVBlocksAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 4);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.blockprefetch2d");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::LLVM::LLVMPointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::LLVM::LLVMPointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseWidth() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseHeight() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBasePitch() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getX() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(4).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getY() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(5).begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseWidthMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseHeightMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBasePitchMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getXMutable() {
    auto range = getODSOperandIndexAndLength(4);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getYMutable() {
    auto range = getODSOperandIndexAndLength(5);
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

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
  }

  uint32_t getTileHeight();
  ::mlir::IntegerAttr getVBlocksAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().v_blocks);
  }

  uint32_t getVBlocks();
  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
  void setElemSizeInBitsAttr(::mlir::IntegerAttr attr) {
    getProperties().elem_size_in_bits = attr;
  }

  void setElemSizeInBits(uint32_t attrValue);
  void setTileWidthAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_width = attr;
  }

  void setTileWidth(uint32_t attrValue);
  void setTileHeightAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_height = attr;
  }

  void setTileHeight(uint32_t attrValue);
  void setVBlocksAttr(::mlir::IntegerAttr attr) {
    getProperties().v_blocks = attr;
  }

  void setVBlocks(uint32_t attrValue);
  void setCacheControlAttr(::mlir::xevm::LoadCacheControlAttr attr) {
    getProperties().cache_control = attr;
  }

  void setCacheControl(::std::optional<::mlir::xevm::LoadCacheControl> attrValue);
  ::mlir::Attribute removeCacheControlAttr() {
      auto attr = getProperties().cache_control;
      getProperties().cache_control = {};
      return attr;
  }

  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::IntegerAttr v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, uint32_t v_blocks, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockPrefetch2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockPrefetch2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  static ::llvm::LogicalResult setPropertiesFromParsedAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
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
  void printProperties(::mlir::MLIRContext *ctx,
          ::mlir::OpAsmPrinter &p, const Properties &prop,
          ::mlir::ArrayRef<::llvm::StringRef> elidedProps) {
    Attribute propAttr = getPropertiesAsAttr(ctx, prop);
    if (propAttr)
      p << "<" << propAttr << ">";
  }

  static ::mlir::ParseResult parseProperties(::mlir::OpAsmParser &parser,
                                   ::mlir::OperationState &result) {
    if (mlir::succeeded(parser.parseOptionalLess())) {
      if (parser.parseAttribute(result.propertiesAttr) || parser.parseGreater())
        return failure();
    }
    return success();
  }


};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::BlockPrefetch2dOp)

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::BlockStore2dOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class BlockStore2dOpGenericAdaptorBase {
public:
  struct Properties {
    using cache_controlTy = ::mlir::xevm::StoreCacheControlAttr;
    cache_controlTy cache_control;

    auto getCacheControl() const {
      auto &propStorage = this->cache_control;
      return ::llvm::dyn_cast_or_null<::mlir::xevm::StoreCacheControlAttr>(propStorage);
    }
    void setCacheControl(const ::mlir::xevm::StoreCacheControlAttr &propValue) {
      this->cache_control = propValue;
    }
    using elem_size_in_bitsTy = ::mlir::IntegerAttr;
    elem_size_in_bitsTy elem_size_in_bits;

    auto getElemSizeInBits() const {
      auto &propStorage = this->elem_size_in_bits;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setElemSizeInBits(const ::mlir::IntegerAttr &propValue) {
      this->elem_size_in_bits = propValue;
    }
    using tile_heightTy = ::mlir::IntegerAttr;
    tile_heightTy tile_height;

    auto getTileHeight() const {
      auto &propStorage = this->tile_height;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileHeight(const ::mlir::IntegerAttr &propValue) {
      this->tile_height = propValue;
    }
    using tile_widthTy = ::mlir::IntegerAttr;
    tile_widthTy tile_width;

    auto getTileWidth() const {
      auto &propStorage = this->tile_width;
      return ::llvm::cast<::mlir::IntegerAttr>(propStorage);
    }
    void setTileWidth(const ::mlir::IntegerAttr &propValue) {
      this->tile_width = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache_control == this->cache_control &&
        rhs.elem_size_in_bits == this->elem_size_in_bits &&
        rhs.tile_height == this->tile_height &&
        rhs.tile_width == this->tile_width &&
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
  BlockStore2dOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.blockstore2d", odsAttrs.getContext());
  }

  BlockStore2dOpGenericAdaptorBase(BlockStore2dOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
    return attr;
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
    return attr;
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    auto attr = ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
    return attr;
  }

  uint32_t getTileHeight();
  ::mlir::xevm::StoreCacheControlAttr getCacheControlAttr() {
    auto attr = ::llvm::dyn_cast_or_null<::mlir::xevm::StoreCacheControlAttr>(getProperties().cache_control);
    return attr;
  }

  ::std::optional<::mlir::xevm::StoreCacheControl> getCacheControl();
};
} // namespace detail
template <typename RangeT>
class BlockStore2dOpGenericAdaptor : public detail::BlockStore2dOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::BlockStore2dOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
  static constexpr int odsIndex_stored_val = 6;
public:
  BlockStore2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  BlockStore2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : BlockStore2dOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  BlockStore2dOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : BlockStore2dOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  BlockStore2dOpGenericAdaptor(RangeT values, const BlockStore2dOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = BlockStore2dOp, typename = std::enable_if_t<std::is_same_v<LateInst, BlockStore2dOp>>>
  BlockStore2dOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  ValueT getBaseWidth() {
    return (*getODSOperands(1).begin());
  }

  ValueT getBaseHeight() {
    return (*getODSOperands(2).begin());
  }

  ValueT getBasePitch() {
    return (*getODSOperands(3).begin());
  }

  ValueT getX() {
    return (*getODSOperands(4).begin());
  }

  ValueT getY() {
    return (*getODSOperands(5).begin());
  }

  ValueT getStoredVal() {
    return (*getODSOperands(6).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class BlockStore2dOpAdaptor : public BlockStore2dOpGenericAdaptor<::mlir::ValueRange> {
public:
  using BlockStore2dOpGenericAdaptor::BlockStore2dOpGenericAdaptor;
  BlockStore2dOpAdaptor(BlockStore2dOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class BlockStore2dOp : public ::mlir::Op<BlockStore2dOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::NOperands<7>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait, ::mlir::MemoryEffectOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = BlockStore2dOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = BlockStore2dOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  static constexpr int odsIndex_base_width = 1;
  static constexpr int odsIndex_base_height = 2;
  static constexpr int odsIndex_base_pitch = 3;
  static constexpr int odsIndex_x = 4;
  static constexpr int odsIndex_y = 5;
  static constexpr int odsIndex_stored_val = 6;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache_control"), ::llvm::StringRef("elem_size_in_bits"), ::llvm::StringRef("tile_height"), ::llvm::StringRef("tile_width")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheControlAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheControlAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getElemSizeInBitsAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getElemSizeInBitsAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  ::mlir::StringAttr getTileHeightAttrName() {
    return getAttributeNameForIndex(2);
  }

  static ::mlir::StringAttr getTileHeightAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 2);
  }

  ::mlir::StringAttr getTileWidthAttrName() {
    return getAttributeNameForIndex(3);
  }

  static ::mlir::StringAttr getTileWidthAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 3);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.blockstore2d");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::LLVM::LLVMPointerType> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::LLVM::LLVMPointerType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseWidth() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBaseHeight() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(2).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getBasePitch() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(3).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getX() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(4).begin());
  }

  ::mlir::TypedValue<::mlir::IntegerType> getY() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::IntegerType>>(*getODSOperands(5).begin());
  }

  ::mlir::TypedValue<::mlir::VectorType> getStoredVal() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*getODSOperands(6).begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseWidthMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBaseHeightMutable() {
    auto range = getODSOperandIndexAndLength(2);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBasePitchMutable() {
    auto range = getODSOperandIndexAndLength(3);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getXMutable() {
    auto range = getODSOperandIndexAndLength(4);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getYMutable() {
    auto range = getODSOperandIndexAndLength(5);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getStoredValMutable() {
    auto range = getODSOperandIndexAndLength(6);
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

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::IntegerAttr getElemSizeInBitsAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().elem_size_in_bits);
  }

  uint32_t getElemSizeInBits();
  ::mlir::IntegerAttr getTileWidthAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_width);
  }

  uint32_t getTileWidth();
  ::mlir::IntegerAttr getTileHeightAttr() {
    return ::llvm::cast<::mlir::IntegerAttr>(getProperties().tile_height);
  }

  uint32_t getTileHeight();
  ::mlir::xevm::StoreCacheControlAttr getCacheControlAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::xevm::StoreCacheControlAttr>(getProperties().cache_control);
  }

  ::std::optional<::mlir::xevm::StoreCacheControl> getCacheControl();
  void setElemSizeInBitsAttr(::mlir::IntegerAttr attr) {
    getProperties().elem_size_in_bits = attr;
  }

  void setElemSizeInBits(uint32_t attrValue);
  void setTileWidthAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_width = attr;
  }

  void setTileWidth(uint32_t attrValue);
  void setTileHeightAttr(::mlir::IntegerAttr attr) {
    getProperties().tile_height = attr;
  }

  void setTileHeight(uint32_t attrValue);
  void setCacheControlAttr(::mlir::xevm::StoreCacheControlAttr attr) {
    getProperties().cache_control = attr;
  }

  void setCacheControl(::std::optional<::mlir::xevm::StoreCacheControl> attrValue);
  ::mlir::Attribute removeCacheControlAttr() {
      auto attr = getProperties().cache_control;
      getProperties().cache_control = {};
      return attr;
  }

  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, ::mlir::IntegerAttr elem_size_in_bits, ::mlir::IntegerAttr tile_width, ::mlir::IntegerAttr tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, ::mlir::Value base_width, ::mlir::Value base_height, ::mlir::Value base_pitch, ::mlir::Value x, ::mlir::Value y, uint32_t elem_size_in_bits, uint32_t tile_width, uint32_t tile_height, ::mlir::Value stored_val, /*optional*/::mlir::xevm::StoreCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockStore2dOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static BlockStore2dOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  static ::llvm::LogicalResult setPropertiesFromParsedAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
  void getEffects(::llvm::SmallVectorImpl<::mlir::SideEffects::EffectInstance<::mlir::MemoryEffects::Effect>> &effects);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 4 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  void printProperties(::mlir::MLIRContext *ctx,
          ::mlir::OpAsmPrinter &p, const Properties &prop,
          ::mlir::ArrayRef<::llvm::StringRef> elidedProps) {
    Attribute propAttr = getPropertiesAsAttr(ctx, prop);
    if (propAttr)
      p << "<" << propAttr << ">";
  }

  static ::mlir::ParseResult parseProperties(::mlir::OpAsmParser &parser,
                                   ::mlir::OperationState &result) {
    if (mlir::succeeded(parser.parseOptionalLess())) {
      if (parser.parseAttribute(result.propertiesAttr) || parser.parseGreater())
        return failure();
    }
    return success();
  }


  /// Default value for v_blocks is 1.
  constexpr uint32_t getVBlocks() {
    return 1;
  }
};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::BlockStore2dOp)

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::MMAOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class MMAOpGenericAdaptorBase {
public:
  struct Properties {
    using shapeTy = ::mlir::xevm::MMAShapeAttr;
    shapeTy shape;

    auto getShape() const {
      auto &propStorage = this->shape;
      return ::llvm::cast<::mlir::xevm::MMAShapeAttr>(propStorage);
    }
    void setShape(const ::mlir::xevm::MMAShapeAttr &propValue) {
      this->shape = propValue;
    }
    using typesTy = ::mlir::xevm::MMATypesAttr;
    typesTy types;

    auto getTypes() const {
      auto &propStorage = this->types;
      return ::llvm::cast<::mlir::xevm::MMATypesAttr>(propStorage);
    }
    void setTypes(const ::mlir::xevm::MMATypesAttr &propValue) {
      this->types = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.shape == this->shape &&
        rhs.types == this->types &&
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
  MMAOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.mma", odsAttrs.getContext());
  }

  MMAOpGenericAdaptorBase(MMAOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize);
  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::xevm::MMAShapeAttr getShapeAttr() {
    auto attr = ::llvm::cast<::mlir::xevm::MMAShapeAttr>(getProperties().shape);
    return attr;
  }

  ::mlir::xevm::MMAShapeAttr getShape();
  ::mlir::xevm::MMATypesAttr getTypesAttr() {
    auto attr = ::llvm::cast<::mlir::xevm::MMATypesAttr>(getProperties().types);
    return attr;
  }

  ::mlir::xevm::MMATypesAttr getTypes();
};
} // namespace detail
template <typename RangeT>
class MMAOpGenericAdaptor : public detail::MMAOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::MMAOpGenericAdaptorBase;
  static constexpr int odsIndex_a = 0;
  static constexpr int odsIndex_b = 1;
  static constexpr int odsIndex_c = 2;
public:
  MMAOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  MMAOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : MMAOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  MMAOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : MMAOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  MMAOpGenericAdaptor(RangeT values, const MMAOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = MMAOp, typename = std::enable_if_t<std::is_same_v<LateInst, MMAOp>>>
  MMAOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getA() {
    return (*getODSOperands(0).begin());
  }

  ValueT getB() {
    return (*getODSOperands(1).begin());
  }

  ValueT getC() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ValueT{} : (*operands.begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class MMAOpAdaptor : public MMAOpGenericAdaptor<::mlir::ValueRange> {
public:
  using MMAOpGenericAdaptor::MMAOpGenericAdaptor;
  MMAOpAdaptor(MMAOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class MMAOp : public ::mlir::Op<MMAOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::OneResult, ::mlir::OpTrait::OneTypedResult<::mlir::VectorType>::Impl, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::AtLeastNOperands<2>::Impl, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = MMAOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = MMAOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_a = 0;
  static constexpr int odsIndex_b = 1;
  static constexpr int odsIndex_c = 2;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("shape"), ::llvm::StringRef("types")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getShapeAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getShapeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getTypesAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getTypesAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.mma");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index);
  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::VectorType> getA() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*getODSOperands(0).begin());
  }

  ::mlir::TypedValue<::mlir::VectorType> getB() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*getODSOperands(1).begin());
  }

  ::mlir::TypedValue<::mlir::VectorType> getC() {
    auto operands = getODSOperands(2);
    return operands.empty() ? ::mlir::TypedValue<::mlir::VectorType>{} : ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*operands.begin());
  }

  ::mlir::OpOperand &getAMutable() {
    auto range = getODSOperandIndexAndLength(0);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::OpOperand &getBMutable() {
    auto range = getODSOperandIndexAndLength(1);
    return getOperation()->getOpOperand(range.first);
  }

  ::mlir::MutableOperandRange getCMutable();
  std::pair<unsigned, unsigned> getODSResultIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::result_range getODSResults(unsigned index) {
    auto valueRange = getODSResultIndexAndLength(index);
    return {std::next(getOperation()->result_begin(), valueRange.first),
             std::next(getOperation()->result_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::VectorType> getD() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::VectorType>>(*getODSResults(0).begin());
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
  ::mlir::xevm::MMAShapeAttr getShapeAttr() {
    return ::llvm::cast<::mlir::xevm::MMAShapeAttr>(getProperties().shape);
  }

  ::mlir::xevm::MMAShapeAttr getShape();
  ::mlir::xevm::MMATypesAttr getTypesAttr() {
    return ::llvm::cast<::mlir::xevm::MMATypesAttr>(getProperties().types);
  }

  ::mlir::xevm::MMATypesAttr getTypes();
  void setShapeAttr(::mlir::xevm::MMAShapeAttr attr) {
    getProperties().shape = attr;
  }

  void setTypesAttr(::mlir::xevm::MMATypesAttr attr) {
    getProperties().types = attr;
  }

  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static MMAOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static MMAOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Type d, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static MMAOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static MMAOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value a, ::mlir::Value b, /*optional*/::mlir::Value c, ::mlir::xevm::MMAShapeAttr shape, ::mlir::xevm::MMATypesAttr types);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static MMAOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static MMAOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static MMAOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static MMAOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  ::llvm::LogicalResult verify();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::MMAOp)

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::MemfenceOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class MemfenceOpGenericAdaptorBase {
public:
  struct Properties {
    using addrspaceTy = ::mlir::xevm::AddrSpaceAttr;
    addrspaceTy addrspace;

    auto getAddrspace() const {
      auto &propStorage = this->addrspace;
      return ::llvm::dyn_cast_or_null<::mlir::xevm::AddrSpaceAttr>(propStorage);
    }
    void setAddrspace(const ::mlir::xevm::AddrSpaceAttr &propValue) {
      this->addrspace = propValue;
    }
    using scopeTy = ::mlir::xevm::MemScopeAttr;
    scopeTy scope;

    auto getScope() const {
      auto &propStorage = this->scope;
      return ::llvm::cast<::mlir::xevm::MemScopeAttr>(propStorage);
    }
    void setScope(const ::mlir::xevm::MemScopeAttr &propValue) {
      this->scope = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.addrspace == this->addrspace &&
        rhs.scope == this->scope &&
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
  MemfenceOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.memfence", odsAttrs.getContext());
  }

  MemfenceOpGenericAdaptorBase(MemfenceOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::xevm::MemScopeAttr getScopeAttr() {
    auto attr = ::llvm::cast<::mlir::xevm::MemScopeAttr>(getProperties().scope);
    return attr;
  }

  ::mlir::xevm::MemScope getScope();
  ::mlir::xevm::AddrSpaceAttr getAddrspaceAttr();
  mlir::xevm::AddrSpace getAddrspace();
};
} // namespace detail
template <typename RangeT>
class MemfenceOpGenericAdaptor : public detail::MemfenceOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::MemfenceOpGenericAdaptorBase;
public:
  MemfenceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  MemfenceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : MemfenceOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  MemfenceOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : MemfenceOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  MemfenceOpGenericAdaptor(RangeT values, const MemfenceOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = MemfenceOp, typename = std::enable_if_t<std::is_same_v<LateInst, MemfenceOp>>>
  MemfenceOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class MemfenceOpAdaptor : public MemfenceOpGenericAdaptor<::mlir::ValueRange> {
public:
  using MemfenceOpGenericAdaptor::MemfenceOpGenericAdaptor;
  MemfenceOpAdaptor(MemfenceOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class MemfenceOp : public ::mlir::Op<MemfenceOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::ZeroOperands, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = MemfenceOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = MemfenceOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("addrspace"), ::llvm::StringRef("scope")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getAddrspaceAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getAddrspaceAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  ::mlir::StringAttr getScopeAttrName() {
    return getAttributeNameForIndex(1);
  }

  static ::mlir::StringAttr getScopeAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 1);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.memfence");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

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
  ::mlir::xevm::MemScopeAttr getScopeAttr() {
    return ::llvm::cast<::mlir::xevm::MemScopeAttr>(getProperties().scope);
  }

  ::mlir::xevm::MemScope getScope();
  ::mlir::xevm::AddrSpaceAttr getAddrspaceAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::xevm::AddrSpaceAttr>(getProperties().addrspace);
  }

  mlir::xevm::AddrSpace getAddrspace();
  void setScopeAttr(::mlir::xevm::MemScopeAttr attr) {
    getProperties().scope = attr;
  }

  void setScope(::mlir::xevm::MemScope attrValue);
  void setAddrspaceAttr(::mlir::xevm::AddrSpaceAttr attr) {
    getProperties().addrspace = attr;
  }

  void setAddrspace(mlir::xevm::AddrSpace attrValue);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScopeAttr scope, ::mlir::xevm::AddrSpaceAttr addrspace = nullptr);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::xevm::MemScope scope, mlir::xevm::AddrSpace addrspace = mlir::xevm::AddrSpace::GENERIC);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static MemfenceOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static MemfenceOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static void populateDefaultProperties(::mlir::OperationName opName, Properties &properties);
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  static ::llvm::LogicalResult setPropertiesFromParsedAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
private:
  ::mlir::StringAttr getAttributeNameForIndex(unsigned index) {
    return getAttributeNameForIndex((*this)->getName(), index);
  }

  static ::mlir::StringAttr getAttributeNameForIndex(::mlir::OperationName name, unsigned index) {
    assert(index < 2 && "invalid attribute index");
    assert(name.getStringRef() == getOperationName() && "invalid operation name");
    assert(name.isRegistered() && "Operation isn't registered, missing a "
          "dependent dialect loading?");
    return name.getAttributeNames()[index];
  }

public:
  void printProperties(::mlir::MLIRContext *ctx,
          ::mlir::OpAsmPrinter &p, const Properties &prop,
          ::mlir::ArrayRef<::llvm::StringRef> elidedProps) {
    Attribute propAttr = getPropertiesAsAttr(ctx, prop);
    if (propAttr)
      p << "<" << propAttr << ">";
  }

  static ::mlir::ParseResult parseProperties(::mlir::OpAsmParser &parser,
                                   ::mlir::OperationState &result) {
    if (mlir::succeeded(parser.parseOptionalLess())) {
      if (parser.parseAttribute(result.propertiesAttr) || parser.parseGreater())
        return failure();
    }
    return success();
  }


};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::MemfenceOp)

namespace mlir {
namespace xevm {

//===----------------------------------------------------------------------===//
// ::mlir::xevm::PrefetchOp declarations
//===----------------------------------------------------------------------===//

namespace detail {
class PrefetchOpGenericAdaptorBase {
public:
  struct Properties {
    using cache_controlTy = ::mlir::xevm::LoadCacheControlAttr;
    cache_controlTy cache_control;

    auto getCacheControl() const {
      auto &propStorage = this->cache_control;
      return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(propStorage);
    }
    void setCacheControl(const ::mlir::xevm::LoadCacheControlAttr &propValue) {
      this->cache_control = propValue;
    }
    bool operator==(const Properties &rhs) const {
      return 
        rhs.cache_control == this->cache_control &&
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
  PrefetchOpGenericAdaptorBase(::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : odsAttrs(attrs), properties(properties), odsRegions(regions) {  if (odsAttrs)
      odsOpName.emplace("xevm.prefetch", odsAttrs.getContext());
  }

  PrefetchOpGenericAdaptorBase(PrefetchOp op);

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index, unsigned odsOperandsSize) {
    return {index, 1};
  }

  const Properties &getProperties() {
    return properties;
  }

  ::mlir::DictionaryAttr getAttributes() {
    return odsAttrs;
  }

  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    auto attr = ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
    return attr;
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
};
} // namespace detail
template <typename RangeT>
class PrefetchOpGenericAdaptor : public detail::PrefetchOpGenericAdaptorBase {
  using ValueT = ::llvm::detail::ValueOfRange<RangeT>;
  using Base = detail::PrefetchOpGenericAdaptorBase;
  static constexpr int odsIndex_ptr = 0;
public:
  PrefetchOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, const Properties &properties, ::mlir::RegionRange regions = {}) : Base(attrs, properties, regions), odsOperands(values) {}

  PrefetchOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs, ::mlir::OpaqueProperties properties, ::mlir::RegionRange regions = {}) : PrefetchOpGenericAdaptor(values, attrs, (properties ? *properties.as<Properties *>() : Properties{}), regions) {}

  PrefetchOpGenericAdaptor(RangeT values, ::mlir::DictionaryAttr attrs = nullptr) : PrefetchOpGenericAdaptor(values, attrs, Properties{}, {}) {}

  PrefetchOpGenericAdaptor(RangeT values, const PrefetchOpGenericAdaptorBase &base) : Base(base), odsOperands(values) {}

  template <typename LateInst = PrefetchOp, typename = std::enable_if_t<std::is_same_v<LateInst, PrefetchOp>>>
  PrefetchOpGenericAdaptor(RangeT values, LateInst op) : Base(op), odsOperands(values) {}

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return Base::getODSOperandIndexAndLength(index, odsOperands.size());
  }

  RangeT getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(odsOperands.begin(), valueRange.first),
             std::next(odsOperands.begin(), valueRange.first + valueRange.second)};
  }

  ValueT getPtr() {
    return (*getODSOperands(0).begin());
  }

  RangeT getOperands() {
    return odsOperands;
  }

private:
  RangeT odsOperands;
};
class PrefetchOpAdaptor : public PrefetchOpGenericAdaptor<::mlir::ValueRange> {
public:
  using PrefetchOpGenericAdaptor::PrefetchOpGenericAdaptor;
  PrefetchOpAdaptor(PrefetchOp op);

  ::llvm::LogicalResult verify(::mlir::Location loc);
};
class PrefetchOp : public ::mlir::Op<PrefetchOp, ::mlir::OpTrait::ZeroRegions, ::mlir::OpTrait::ZeroResults, ::mlir::OpTrait::ZeroSuccessors, ::mlir::OpTrait::OneOperand, ::mlir::OpTrait::OpInvariants, ::mlir::BytecodeOpInterface::Trait> {
public:
  using Op::Op;
  using Op::print;
  using Adaptor = PrefetchOpAdaptor;
  template <typename RangeT>
  using GenericAdaptor = PrefetchOpGenericAdaptor<RangeT>;
  using FoldAdaptor = GenericAdaptor<::llvm::ArrayRef<::mlir::Attribute>>;
  static constexpr int odsIndex_ptr = 0;
  using Properties = FoldAdaptor::Properties;
  static ::llvm::ArrayRef<::llvm::StringRef> getAttributeNames() {
    static ::llvm::StringRef attrNames[] = {::llvm::StringRef("cache_control")};
    return ::llvm::ArrayRef(attrNames);
  }

  ::mlir::StringAttr getCacheControlAttrName() {
    return getAttributeNameForIndex(0);
  }

  static ::mlir::StringAttr getCacheControlAttrName(::mlir::OperationName name) {
    return getAttributeNameForIndex(name, 0);
  }

  static constexpr ::llvm::StringLiteral getOperationName() {
    return ::llvm::StringLiteral("xevm.prefetch");
  }

  std::pair<unsigned, unsigned> getODSOperandIndexAndLength(unsigned index) {
    return {index, 1};
  }

  ::mlir::Operation::operand_range getODSOperands(unsigned index) {
    auto valueRange = getODSOperandIndexAndLength(index);
    return {std::next(getOperation()->operand_begin(), valueRange.first),
             std::next(getOperation()->operand_begin(), valueRange.first + valueRange.second)};
  }

  ::mlir::TypedValue<::mlir::Type> getPtr() {
    return ::llvm::cast<::mlir::TypedValue<::mlir::Type>>(*getODSOperands(0).begin());
  }

  ::mlir::OpOperand &getPtrMutable() {
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

  static ::llvm::LogicalResult setPropertiesFromAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::mlir::Attribute getPropertiesAsAttr(::mlir::MLIRContext *ctx, const Properties &prop);
  static llvm::hash_code computePropertiesHash(const Properties &prop);
  static std::optional<mlir::Attribute> getInherentAttr(::mlir::MLIRContext *ctx, const Properties &prop, llvm::StringRef name);
  static void setInherentAttr(Properties &prop, llvm::StringRef name, mlir::Attribute value);
  static void populateInherentAttrs(::mlir::MLIRContext *ctx, const Properties &prop, ::mlir::NamedAttrList &attrs);
  static ::llvm::LogicalResult verifyInherentAttrs(::mlir::OperationName opName, ::mlir::NamedAttrList &attrs, llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  static ::llvm::LogicalResult readProperties(::mlir::DialectBytecodeReader &reader, ::mlir::OperationState &state);
  void writeProperties(::mlir::DialectBytecodeWriter &writer);
  ::mlir::xevm::LoadCacheControlAttr getCacheControlAttr() {
    return ::llvm::dyn_cast_or_null<::mlir::xevm::LoadCacheControlAttr>(getProperties().cache_control);
  }

  ::std::optional<::mlir::xevm::LoadCacheControl> getCacheControl();
  void setCacheControlAttr(::mlir::xevm::LoadCacheControlAttr attr) {
    getProperties().cache_control = attr;
  }

  void setCacheControl(::std::optional<::mlir::xevm::LoadCacheControl> attrValue);
  ::mlir::Attribute removeCacheControlAttr() {
      auto attr = getProperties().cache_control;
      getProperties().cache_control = {};
      return attr;
  }

  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static PrefetchOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static PrefetchOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &odsBuilder, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static PrefetchOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static PrefetchOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::Value ptr, /*optional*/::mlir::xevm::LoadCacheControlAttr cache_control);
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static PrefetchOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static PrefetchOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, ::llvm::ArrayRef<::mlir::NamedAttribute> attributes = {});
  static void build(::mlir::OpBuilder &, ::mlir::OperationState &odsState, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static PrefetchOp create(::mlir::OpBuilder &builder, ::mlir::Location location, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  static PrefetchOp create(::mlir::ImplicitLocOpBuilder &builder, ::mlir::TypeRange resultTypes, ::mlir::ValueRange operands, const Properties &properties, ::llvm::ArrayRef<::mlir::NamedAttribute> discardableAttributes = {});
  ::llvm::LogicalResult verifyInvariantsImpl();
  ::llvm::LogicalResult verifyInvariants();
  static ::mlir::ParseResult parse(::mlir::OpAsmParser &parser, ::mlir::OperationState &result);
  static ::llvm::LogicalResult setPropertiesFromParsedAttr(Properties &prop, ::mlir::Attribute attr, ::llvm::function_ref<::mlir::InFlightDiagnostic()> emitError);
  void print(::mlir::OpAsmPrinter &_odsPrinter);
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
  void printProperties(::mlir::MLIRContext *ctx,
          ::mlir::OpAsmPrinter &p, const Properties &prop,
          ::mlir::ArrayRef<::llvm::StringRef> elidedProps) {
    Attribute propAttr = getPropertiesAsAttr(ctx, prop);
    if (propAttr)
      p << "<" << propAttr << ">";
  }

  static ::mlir::ParseResult parseProperties(::mlir::OpAsmParser &parser,
                                   ::mlir::OperationState &result) {
    if (mlir::succeeded(parser.parseOptionalLess())) {
      if (parser.parseAttribute(result.propertiesAttr) || parser.parseGreater())
        return failure();
    }
    return success();
  }


};
} // namespace xevm
} // namespace mlir
MLIR_DECLARE_EXPLICIT_TYPE_ID(::mlir::xevm::PrefetchOp)


#endif  // GET_OP_CLASSES

