/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir {
namespace triton {
namespace nvws {
class DescriptorLoadOpInterface;
namespace detail {
struct DescriptorLoadOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    int (*getTxCount)(const Concept *impl, ::mlir::Operation *);
    /// The base classes of this interface.
    const ::mlir::triton::DescriptorOpInterface::Concept *implDescriptorOpInterface = nullptr;

    void initializeInterfaceConcept(::mlir::detail::InterfaceMap &interfaceMap) {
      implDescriptorOpInterface = interfaceMap.lookup<::mlir::triton::DescriptorOpInterface>();
      assert(implDescriptorOpInterface && "`::mlir::triton::nvws::DescriptorLoadOpInterface` expected its base interface `::mlir::triton::DescriptorOpInterface` to be registered");
    }
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::triton::nvws::DescriptorLoadOpInterface;
    Model() : Concept{getTxCount} {}

    static inline int getTxCount(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::triton::nvws::DescriptorLoadOpInterface;
    FallbackModel() : Concept{getTxCount} {}

    static inline int getTxCount(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct DescriptorLoadOpInterfaceTrait;

} // namespace detail
class DescriptorLoadOpInterface : public ::mlir::OpInterface<DescriptorLoadOpInterface, detail::DescriptorLoadOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<DescriptorLoadOpInterface, detail::DescriptorLoadOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::DescriptorLoadOpInterfaceTrait<ConcreteOp> {};

  /// Get the transaction counts
  int getTxCount();
  //===----------------------------------------------------------------===//
  // Inherited from ::mlir::triton::DescriptorOpInterface
  //===----------------------------------------------------------------===//

  operator ::mlir::triton::DescriptorOpInterface () const {
    if (!*this) return nullptr;
    return ::mlir::triton::DescriptorOpInterface(*this, getImpl()->implDescriptorOpInterface);
  }


  /// Get the descriptor
  ::mlir::TypedValue<mlir::triton::TensorDescType> getDesc();
};
namespace detail {
  template <typename ConcreteOp>
  struct DescriptorLoadOpInterfaceTrait : public ::mlir::OpInterface<DescriptorLoadOpInterface, detail::DescriptorLoadOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };
}// namespace detail
} // namespace nvws
} // namespace triton
} // namespace mlir
namespace mlir {
namespace triton {
namespace nvws {
template<typename ConcreteOp>
int detail::DescriptorLoadOpInterfaceInterfaceTraits::Model<ConcreteOp>::getTxCount(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getTxCount();
}
template<typename ConcreteOp>
int detail::DescriptorLoadOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getTxCount(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getTxCount(tablegen_opaque_val);
}
} // namespace nvws
} // namespace triton
} // namespace mlir
