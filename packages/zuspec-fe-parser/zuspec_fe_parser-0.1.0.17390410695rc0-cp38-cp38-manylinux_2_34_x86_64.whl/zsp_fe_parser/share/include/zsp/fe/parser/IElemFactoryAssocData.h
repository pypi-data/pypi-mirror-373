/**
 * IElemFactoryAssocData.h
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
#include "vsc/dm/ITypeField.h"
#include "zsp/ast/IAssocData.h"
#include "zsp/fe/parser/IAst2ArlContext.h"

namespace zsp {
namespace fe {
namespace parser {



class IElemFactoryAssocData : public virtual ast::IAssocData {
public:

    virtual ~IElemFactoryAssocData() { }

    virtual vsc::dm::ITypeField *mkTypeFieldPhy(
        IAst2ArlContext         *ctx,
        const std::string       &name,
        ast::IScopeChild        *type,
        vsc::dm::TypeFieldAttr  attr,
        vsc::dm::ITypeExpr      *init) = 0;

    virtual vsc::dm::ITypeField *mkTypeFieldArr(
        IAst2ArlContext         *ctx,
        const std::string       &name,
        ast::IScopeChild        *type,
        ast::IScopeChild        *elem_type,
        ast::IExpr              *size,
        vsc::dm::TypeFieldAttr  attr,
        vsc::dm::ITypeExpr      *init) = 0;

    virtual vsc::dm::ITypeField *mkTypeFieldList(
        IAst2ArlContext         *ctx,
        const std::string       &name,
        ast::IScopeChild        *type,
        ast::IScopeChild        *elem_type,
        vsc::dm::TypeFieldAttr  attr,
        vsc::dm::ITypeExpr      *init) = 0;
    
    virtual vsc::dm::IDataType *mkDataType(
        IAst2ArlContext         *ctx,
        const std::string       &name,
        ast::IScopeChild        *type) = 0;

};

} /* namespace parser */
} /* namespace fe */
} /* namespace zsp */


