/**
 * IAst2ArlBuilder.h
 *
 * Copyright 2022 Matthew Ballance and Contributors
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may 
 * not use this file except in compliance with the License.  
 * You may obtain a copy of the License at:
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software 
 * distributed under the License is distributed on an "AS IS" BASIS, 
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
 * See the License for the specific language governing permissions and 
 * limitations under the License.
 *
 * Created on:
 *     Author: 
 */
#pragma once
#include <memory>
#include "zsp/arl/dm/IContext.h"
#include "zsp/ast/ISymbolScope.h"
#include "zsp/fe/parser/IAst2ArlContext.h"
#include "zsp/parser/IMarkerListener.h"

namespace zsp {
namespace fe {
namespace parser {


class IAst2ArlBuilder;
using IAst2ArlBuilderUP=std::unique_ptr<IAst2ArlBuilder>;
class IAst2ArlBuilder {
public:

    virtual ~IAst2ArlBuilder() { }

    virtual void build(
        ast::ISymbolScope               *root,
        IAst2ArlContext                 *ctxt) = 0;

};

} /* namespace parser */
} /* namespace fe */
} /* namespace zsp */


