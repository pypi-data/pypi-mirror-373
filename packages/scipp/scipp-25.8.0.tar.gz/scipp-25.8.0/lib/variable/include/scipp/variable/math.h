// SPDX-License-Identifier: BSD-3-Clause
// Copyright (c) 2023 Scipp contributors (https://github.com/scipp)
/// @file
/// @author Simon Heybrock
#pragma once

#include "scipp-variable_export.h"
#include "scipp/variable/variable.h"

#include "scipp/variable/generated_math.h"

namespace scipp::variable {
[[nodiscard]] SCIPP_VARIABLE_EXPORT Variable
midpoints(const Variable &var, std::optional<Dim> dim = std::nullopt);
} // namespace scipp::variable
