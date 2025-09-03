/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace xegpu {
/// Common trait for all XeGPU layouts.
class LayoutTrait;
namespace detail {
struct LayoutTraitInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    int64_t (*getRank)(const Concept *impl, ::mlir::Attribute );
    std::optional<SmallVector<int64_t>> (*getSgLayoutAsInt)(const Concept *impl, ::mlir::Attribute );
    std::optional<SmallVector<int64_t>> (*getSgDataAsInt)(const Concept *impl, ::mlir::Attribute );
    FailureOr<SmallVector<Value>> (*delinearizeSubgroupId)(const Concept *impl, ::mlir::Attribute , OpBuilder &, Location, Value);
    FailureOr<SmallVector<SmallVector<Value>>> (*getOffsets)(const Concept *impl, ::mlir::Attribute , OpBuilder &, Location, Value, ArrayRef<int64_t>);
  };
  template<typename ConcreteAttr>
  class Model : public Concept {
  public:
    using Interface = ::mlir::xegpu::LayoutTrait;
    Model() : Concept{getRank, getSgLayoutAsInt, getSgDataAsInt, delinearizeSubgroupId, getOffsets} {}

    static inline int64_t getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline std::optional<SmallVector<int64_t>> getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline std::optional<SmallVector<int64_t>> getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline FailureOr<SmallVector<Value>> delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId);
    static inline FailureOr<SmallVector<SmallVector<Value>>> getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape);
  };
  template<typename ConcreteAttr>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::xegpu::LayoutTrait;
    FallbackModel() : Concept{getRank, getSgLayoutAsInt, getSgDataAsInt, delinearizeSubgroupId, getOffsets} {}

    static inline int64_t getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline std::optional<SmallVector<int64_t>> getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline std::optional<SmallVector<int64_t>> getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val);
    static inline FailureOr<SmallVector<Value>> delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId);
    static inline FailureOr<SmallVector<SmallVector<Value>>> getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape);
  };
  template<typename ConcreteModel, typename ConcreteAttr>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteAttr;
  };
};
template <typename ConcreteAttr>
struct LayoutTraitTrait;

} // namespace detail
class LayoutTrait : public ::mlir::AttributeInterface<LayoutTrait, detail::LayoutTraitInterfaceTraits> {
public:
  using ::mlir::AttributeInterface<LayoutTrait, detail::LayoutTraitInterfaceTraits>::AttributeInterface;
  template <typename ConcreteAttr>
  struct Trait : public detail::LayoutTraitTrait<ConcreteAttr> {};

  /// Get the rank of attribute
  int64_t getRank() const;

  /// Get the SgLayout field of the attribute as integer array
  std::optional<SmallVector<int64_t>> getSgLayoutAsInt() const;

  /// Get the SgData field of the attribute as integer array
  std::optional<SmallVector<int64_t>> getSgDataAsInt() const;

  /// Delinearizes a linear subgroup ID into its multidimensional
  ///                       indices based on the effective subgroup layout.
  FailureOr<SmallVector<Value>> delinearizeSubgroupId(OpBuilder & builder, Location loc, Value linearId) const;

  /// Generates instructions to compute multidimensional offsets for blocks
  ///                       assigned to a subgroup identified by linearId. The shape parameter
  ///                       represents the workgroup-level problem size. Each subgroup may access
  ///                       multiple blocks according to round-robin distribution rules.
  FailureOr<SmallVector<SmallVector<Value>>> getOffsets(OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) const;
};
namespace detail {
  template <typename ConcreteAttr>
  struct LayoutTraitTrait : public ::mlir::AttributeInterface<LayoutTrait, detail::LayoutTraitInterfaceTraits>::Trait<ConcreteAttr> {
  };
}// namespace detail
} // namespace xegpu
} // namespace mlir
namespace mlir {
namespace xegpu {
template<typename ConcreteAttr>
int64_t detail::LayoutTraitInterfaceTraits::Model<ConcreteAttr>::getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getRank();
}
template<typename ConcreteAttr>
std::optional<SmallVector<int64_t>> detail::LayoutTraitInterfaceTraits::Model<ConcreteAttr>::getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getSgLayoutAsInt();
}
template<typename ConcreteAttr>
std::optional<SmallVector<int64_t>> detail::LayoutTraitInterfaceTraits::Model<ConcreteAttr>::getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getSgDataAsInt();
}
template<typename ConcreteAttr>
FailureOr<SmallVector<Value>> detail::LayoutTraitInterfaceTraits::Model<ConcreteAttr>::delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).delinearizeSubgroupId(builder, loc, linearId);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<SmallVector<Value>>> detail::LayoutTraitInterfaceTraits::Model<ConcreteAttr>::getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) {
  return (::llvm::cast<ConcreteAttr>(tablegen_opaque_val)).getOffsets(builder, loc, linearId, shape);
}
template<typename ConcreteAttr>
int64_t detail::LayoutTraitInterfaceTraits::FallbackModel<ConcreteAttr>::getRank(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getRank(tablegen_opaque_val);
}
template<typename ConcreteAttr>
std::optional<SmallVector<int64_t>> detail::LayoutTraitInterfaceTraits::FallbackModel<ConcreteAttr>::getSgLayoutAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getSgLayoutAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
std::optional<SmallVector<int64_t>> detail::LayoutTraitInterfaceTraits::FallbackModel<ConcreteAttr>::getSgDataAsInt(const Concept *impl, ::mlir::Attribute tablegen_opaque_val) {
  return static_cast<const ConcreteAttr *>(impl)->getSgDataAsInt(tablegen_opaque_val);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<Value>> detail::LayoutTraitInterfaceTraits::FallbackModel<ConcreteAttr>::delinearizeSubgroupId(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId) {
  return static_cast<const ConcreteAttr *>(impl)->delinearizeSubgroupId(tablegen_opaque_val, builder, loc, linearId);
}
template<typename ConcreteAttr>
FailureOr<SmallVector<SmallVector<Value>>> detail::LayoutTraitInterfaceTraits::FallbackModel<ConcreteAttr>::getOffsets(const Concept *impl, ::mlir::Attribute tablegen_opaque_val, OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) {
  return static_cast<const ConcreteAttr *>(impl)->getOffsets(tablegen_opaque_val, builder, loc, linearId, shape);
}
} // namespace xegpu
} // namespace mlir
