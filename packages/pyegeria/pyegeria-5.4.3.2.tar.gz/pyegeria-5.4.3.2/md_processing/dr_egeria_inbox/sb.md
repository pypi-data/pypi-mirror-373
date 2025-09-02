<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright Contributors to the Egeria project. -->

# Rules 
* If this is a create, and qualfied name is provided, it will be used.
* If this is an update, and qualified name is provided, it is an error if it doesn't match.
* If this is an update and no qualified name provided, will try to use the display name
* If this is an update and qualified name and guid provided, then the qualified name can be changed


# Update Solution Blueprint

## Display Name

Clinical Trial Management Solution Blueprint

## Description

A description of how a clinical trial is managed in Coco Pharmaceuticals.

## Version Identifier

V1.2
## Qualified Name

SolutionBlueprint:Clinical Trial Management Solution Blueprint:V1.2

## <guid>

---

# Update Solution Component

## Display Name

Hospital Processes

## Description

## Version Identifier

## Solution Component Type
String - valid value?
## Planned Deployed Implementation Type
String - valid value?
## Solution Blueprints

Clinical Trial Management Solution Blueprint

## Parent Components

---

# Create Solution Component

## Display Name

Lab Processes

## Description

## Version Identifier

## Solution Component Type
String - valid value?
## Planned Deployed Implementation Type
String - valid value?
## Solution Blueprints

SolutionBlueprint:Clinical Trial Management Solution Blueprint:V1.2

## Parent Components

---

# Create Solution Role

## Name

## Identifier
str
## Description

## Scope
str - valid values 
---

# Create Solution Actor Role 

## Solution Component

SolutionComponent:XXX q_name
<required>
## Actor

Actor:XXX -q_name
<required>
## Role
str - valid value
<required>
## Description


---

# Create Solution Linking Role

## Starting Solution Component
q_name of soln
<required>
## Wired To Solution Component
q_name of soln
<required>
## Label
str
<required>
## Description
str
## Information Supply Chain Segment GUIDs
