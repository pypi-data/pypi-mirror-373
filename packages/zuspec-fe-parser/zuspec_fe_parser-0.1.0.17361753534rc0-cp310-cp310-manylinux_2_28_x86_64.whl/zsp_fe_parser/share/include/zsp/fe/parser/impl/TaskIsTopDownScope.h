/**
 * TaskIsTopDownScope.h
 *
 * Copyright 2023 Matthew Ballance and Contributors
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
#include "zsp/ast/impl/VisitorBase.h"

namespace zsp {
namespace fe {
namespace parser {



class TaskIsTopDownScope : public virtual ast::VisitorBase {
public:

    virtual ~TaskIsTopDownScope() { }

    bool check(ast::IScopeChild *s) {
        m_is = false;
        s->accept(m_this);
        return m_is;
    }

    virtual void visitSymbolTypeScope(ast::ISymbolTypeScope *i) override {
        m_is = true;
    }

    virtual void visitSymbolFunctionScope(ast::ISymbolFunctionScope *i) override { }

private:
    bool                m_is;
};

} /* namespace parser */
} /* namespace fe */
} /* namespace zsp */


