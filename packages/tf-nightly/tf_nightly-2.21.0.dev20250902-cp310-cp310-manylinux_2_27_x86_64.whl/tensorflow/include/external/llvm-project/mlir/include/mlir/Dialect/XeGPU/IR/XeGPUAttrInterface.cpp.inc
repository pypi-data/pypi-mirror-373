/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/


/// Get the rank of attribute
int64_t mlir::xegpu::LayoutTrait::getRank() const {
      return getImpl()->getRank(getImpl(), *this);
  }

/// Get the SgLayout field of the attribute as integer array
std::optional<SmallVector<int64_t>> mlir::xegpu::LayoutTrait::getSgLayoutAsInt() const {
      return getImpl()->getSgLayoutAsInt(getImpl(), *this);
  }

/// Get the SgData field of the attribute as integer array
std::optional<SmallVector<int64_t>> mlir::xegpu::LayoutTrait::getSgDataAsInt() const {
      return getImpl()->getSgDataAsInt(getImpl(), *this);
  }

/// Delinearizes a linear subgroup ID into its multidimensional
///                       indices based on the effective subgroup layout.
FailureOr<SmallVector<Value>> mlir::xegpu::LayoutTrait::delinearizeSubgroupId(OpBuilder & builder, Location loc, Value linearId) const {
      return getImpl()->delinearizeSubgroupId(getImpl(), *this, builder, loc, linearId);
  }

/// Generates instructions to compute multidimensional offsets for blocks
///                       assigned to a subgroup identified by linearId. The shape parameter
///                       represents the workgroup-level problem size. Each subgroup may access
///                       multiple blocks according to round-robin distribution rules.
FailureOr<SmallVector<SmallVector<Value>>> mlir::xegpu::LayoutTrait::getOffsets(OpBuilder & builder, Location loc, Value linearId, ArrayRef<int64_t> shape) const {
      return getImpl()->getOffsets(getImpl(), *this, builder, loc, linearId, shape);
  }
