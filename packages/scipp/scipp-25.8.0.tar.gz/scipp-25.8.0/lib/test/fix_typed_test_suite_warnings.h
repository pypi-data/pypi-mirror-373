// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2023 Scipp contributors (https://github.com/scipp)

#pragma once
#include <gtest/gtest-typed-test.h>

// Originally definition of this macro in gtest contains ellipsis
// TYPED_TEST_SUITE(CaseName, Types, ...)
// that obligate to pass at least 3 args to macro, using 2 args
// leads to the warning, macro is redefined here to avoid this,
// as long as it is not used with more then 2 args anywhere
#undef TYPED_TEST_SUITE
#define TYPED_TEST_SUITE(CaseName, Types)                                      \
  typedef ::testing::internal::GenerateTypeList<Types>::type                   \
      GTEST_TYPE_PARAMS_(CaseName);                                            \
  typedef ::testing::internal::NameGeneratorSelector<>::type                   \
  GTEST_NAME_GENERATOR_(CaseName)
