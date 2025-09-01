/**
 * IAst2ArlContext.h
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
#include "dmgr/IDebugMgr.h"
#include "vsc/dm/ITypeExpr.h"
#include "zsp/parser/IFactory.h"
#include "zsp/parser/impl/ScopeUtil.h"
#include "zsp/arl/dm/IContext.h"
#include "zsp/ast/IScopeChild.h"

namespace zsp {
namespace fe {
namespace parser {


class IAst2ArlContext;
using IAst2ArlContextUP=std::unique_ptr<IAst2ArlContext>;
class IAst2ArlContext {
public:

    virtual ~IAst2ArlContext() { }

    virtual dmgr::IDebugMgr *getDebugMgr() const = 0;

    virtual zsp::parser::IFactory *factory() const = 0;

    virtual arl::dm::IContext *ctxt() const = 0;

    virtual ast::ISymbolChildrenScope *symScope() const = 0;

    template <class T> T *symScopeT() const {
        return dynamic_cast<T *>(symScope());
    }

    virtual ast::ISymbolChildrenScope *rootSymScope() const = 0;

    template <class T> T *rootSymScopeT() const {
        return dynamic_cast<T *>(rootSymScope());
    }

    virtual const std::vector<zsp::parser::ScopeUtil> &symScopes() const = 0;

    virtual void pushSymScope(ast::IScopeChild *s) = 0;

    virtual void popSymScope() = 0;

    virtual void pushSymScopeStack(ast::ISymbolChildrenScope *s=0) = 0;

    virtual void popSymScopeStack() = 0;

    virtual ast::IScopeChild *resolveRefPath(const ast::ISymbolRefPath *ref) = 0;

    virtual int32_t findBottomUpScope(ast::IScopeChild *scope) = 0;

    virtual ast::ISymbolScope *inlineCtxt() const = 0;

    virtual void pushInlineCtxt(ast::ISymbolScope *s) = 0;

    virtual void popInlineCtxt() = 0;

    virtual ast::ISymbolScope *typeScope() const = 0;

    virtual vsc::dm::IAccept *findType(ast::IScopeChild *t) = 0;

    template <class T> T *findTypeT(ast::IScopeChild *t) {
        return dynamic_cast<T *>(findType(t));
    }

    virtual void addType(ast::IScopeChild *t, vsc::dm::IAccept *dmt) = 0;

    virtual vsc::dm::IAccept *getType(ast::IScopeChild *t) = 0;

    virtual ast::IScopeChild *getTypeAst(vsc::dm::IAccept *dmt) = 0;

    template <class T> T *getTypeT(ast::IScopeChild *t) {
        return dynamic_cast<T *>(getType(t));
    }

    virtual std::string getQName(const std::string &name) = 0;

    virtual ast::ISymbolScope *getRoot() = 0;

    virtual void pushIsPyRef(bool v) = 0;

    virtual void setIsPyRef(bool v) = 0;

    virtual bool isPyRef() = 0;

    virtual void popIsPyRef() = 0;

    virtual void pushBaseExpr(vsc::dm::ITypeExpr *expr) = 0;
    
    virtual vsc::dm::ITypeExpr *baseExpr() = 0;

    virtual vsc::dm::ITypeExpr *popBaseExpr() = 0;

};

} /* namespace parser */
} /* namespace fe */
} /* namespace zsp */


