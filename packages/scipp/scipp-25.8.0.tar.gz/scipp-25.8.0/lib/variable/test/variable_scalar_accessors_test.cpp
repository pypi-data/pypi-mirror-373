// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
#include <gtest/gtest.h>

#include "scipp/core/except.h"
#include "scipp/variable/variable.h"
#include "test_macros.h"

using namespace scipp;

template <typename T>
class Variable_scalar_accessors_mutate : public ::testing::Test {
protected:
  template <class V> T access(V &variable) { return variable; }
};
template <typename T> class Variable_scalar_accessors : public ::testing::Test {
protected:
  template <class V> T access(V &variable) { return variable; }
};

using VariableTypesMutable = ::testing::Types<Variable &>;

using VariableTypes = ::testing::Types<Variable &, const Variable &>;

TYPED_TEST_SUITE(Variable_scalar_accessors_mutate, VariableTypesMutable);
TYPED_TEST_SUITE(Variable_scalar_accessors, VariableTypes);

TYPED_TEST(Variable_scalar_accessors_mutate, value_dim_0) {
  auto v_ = makeVariable<double>(Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template value<float>(), except::TypeError);
  ASSERT_THROW(v.template variance<double>(), except::VariancesError);
  EXPECT_EQ(v.template value<double>(), 1.1);
  v.template value<double>() *= 2;
  EXPECT_EQ(v.template value<double>(), 2.2);
}

TYPED_TEST(Variable_scalar_accessors_mutate, variance_dim_0) {
  auto v_ = makeVariable<double>(Values{1.1}, Variances{2.2});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template variance<float>(), except::TypeError);
  EXPECT_EQ(v.template variance<double>(), 2.2);
  v.template variance<double>() *= 2;
  EXPECT_EQ(v.template variance<double>(), 4.4);
}

TYPED_TEST(Variable_scalar_accessors, value_dim_0) {
  auto v_ = makeVariable<double>(Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template value<float>(), except::TypeError);
  ASSERT_THROW(v.template variance<double>(), except::VariancesError);
  EXPECT_EQ(v.template value<double>(), 1.1);
}

TYPED_TEST(Variable_scalar_accessors, variance_dim_0) {
  auto v_ = makeVariable<double>(Values{1.1}, Variances{2.2});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template variance<float>(), except::TypeError);
  EXPECT_EQ(v.template variance<double>(), 2.2);
}

TYPED_TEST(Variable_scalar_accessors, value_dim_1) {
  auto v_ = makeVariable<double>(Dims{Dim::X}, Shape{1}, Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template value<double>(), except::DimensionError);
}

TYPED_TEST(Variable_scalar_accessors, variance_dim_1) {
  auto v_ =
      makeVariable<double>(Dims{Dim::X}, Shape{1}, Values{1.1}, Variances{2.2});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW(v.template value<double>(), except::DimensionError);
  ASSERT_THROW(v.template variance<double>(), except::DimensionError);
}

TYPED_TEST(Variable_scalar_accessors, dim_dim_1) {
  auto v_ = variable::makeVariable<double>(Dims{Dim::X}, Shape{1}, Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_EQ(v.dim(), Dim::X);
}

TYPED_TEST(Variable_scalar_accessors, dim_dim_0) {
  auto v_ = variable::makeVariable<double>(Dims{}, Shape{}, Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW_DISCARD(v.dim(), except::DimensionError);
}

TYPED_TEST(Variable_scalar_accessors, dim_dim_2) {
  auto v_ = variable::makeVariable<double>(Dims{Dim::X, Dim::Y}, Shape{1, 1},
                                           Values{1.1});
  auto &&v = TestFixture::access(v_);
  ASSERT_THROW_DISCARD(v.dim(), except::DimensionError);
}
