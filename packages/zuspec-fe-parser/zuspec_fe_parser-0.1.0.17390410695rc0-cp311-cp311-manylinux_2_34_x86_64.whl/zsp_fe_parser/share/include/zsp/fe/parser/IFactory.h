/**
 * IFactory.h
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
#include "dmgr/IDebugMgr.h"
#include "zsp/parser/IFactory.h"
#include "zsp/parser/IMarkerListener.h"
#include "zsp/fe/parser/IAst2ArlBuilder.h"
#include "zsp/fe/parser/IAst2ArlContext.h"

namespace zsp {
namespace fe {
namespace parser {

class IFactory {
public:

    virtual ~IFactory() { }

    virtual void init(
        dmgr::IDebugMgr         *dmgr,
        zsp::parser::IFactory   *factory) = 0;

    virtual dmgr::IDebugMgr *getDebugMgr() = 0;

    virtual IAst2ArlBuilder *mkAst2ArlBuilder() = 0;

    virtual IAst2ArlContext *mkAst2ArlContext(
        arl::dm::IContext               *ctxt,
        ast::ISymbolScope               *root,
        zsp::parser::IMarkerListener    *marker_l) = 0;

};

} /* namespace parser */
} /* namespace fe */
} /* namespace zsp */


