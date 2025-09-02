// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
/// @file
/// @author Owen Arnold
#include <string>

#include "scipp/core/except.h"
#include "scipp/core/slice.h"

namespace scipp::core {

namespace {
void validate_begin(const scipp::index begin) {
  if (begin < 0)
    throw except::SliceError("begin must be >= 0. Given " +
                             std::to_string(begin));
}
} // namespace

/// Constructor for range slice
/// \param dim_ Slice Dimension
/// \param begin_ start index or single index of the slice
/// \param end_ end index for the range. Note that -1 indicates a point slice,
/// not before-end.
///
Slice::Slice(const Dim dim_, const scipp::index begin_, const scipp::index end_,
             const scipp::index stride_)
    : m_dim(dim_), m_begin(begin_), m_end(end_), m_stride(stride_) {
  validate_begin(begin_);
  if (end_ != -1 && begin_ > end_)
    throw except::SliceError("end must be >= begin. Given begin " +
                             std::to_string(begin_) + " end " +
                             std::to_string(end_));
  if (stride_ == 0)
    throw except::SliceError("slice step cannot be zero");
  if (stride_ < 0)
    throw except::SliceError("negative slice step support not implemented");
}

/// Constructor for point slice
/// \param dim_ Slice Dimension
/// \param begin_ start index or single index of the slice
///
Slice::Slice(const Dim dim_, const index begin_)
    : m_dim(dim_), m_begin(begin_), m_end(-1), m_stride(1) {
  validate_begin(begin_);
}

bool Slice::operator==(const Slice &other) const noexcept {
  return m_dim == other.dim() && m_begin == other.m_begin &&
         m_end == other.m_end && m_stride == other.m_stride;
}
bool Slice::operator!=(const Slice &other) const noexcept {
  return !(*this == other);
}

} // namespace scipp::core
