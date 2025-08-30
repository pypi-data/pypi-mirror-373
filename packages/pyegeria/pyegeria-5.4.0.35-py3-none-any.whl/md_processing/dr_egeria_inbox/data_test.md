




___

Data Specification for the Teddy Bear Drop Foot Clinical Trial
___

# Create Data Specification

## Data Specification

Data Specification for the Teddy Bear Drop Foot Clinical Trial

##  Description

Principle data requirements for Teddy Bear Drop Foot clinical trial.
___

#  Create Data Specification

## Data Specification
Data Specification for the Werewolf Transformation Clinical Trial

##  Description

Principle data requirements for Werewolf Transformation clinical trial.

#  Create Data Specification

## Data Specification
Test Spec

##  Description

for testing purposes only.



#  Create Data Dictionary
## Name
Clinical Trial Data Dictionary

## Description
A data dictionary for clinical trial data elements.


#  Create Data Dictionary
## Name
Pharma Data Dictionary

## Description
A data dictionary of elements relevant to the Pharma communities.


___


___

TBDF-Incoming Weekly Measurement Data
___

#  Create Data Structure

## Data Structure

TBDF-Incoming Weekly Measurement Data

## Description
This describes the weekly measurement data for each patient in the Teddy Bear drop foot clinical trial

## In Data Specification
Data Specification for the Teddy Bear Drop Foot Clinical Trial, Test Spec


## Qualified Name


___

WWT-Incoming Weekly Measurement Data

#  Create Data Structure

## Qualified Name
DataStruct::WWT-Incoming Weekly Measurement Data

## GUID


## Data Structure

WWT-Incoming Weekly Measurement Data


##  Description
A collection of data fields that form a data structure.
Meow

##  In Data Specification

Test Spec
Data Specification for the Teddy Bear Drop Foot Clinical Trial

##  Qualified Name
___



# foo Create Data Field
## Name
PatientId
## Description
Unique identifier of the patient
## Data Type
String
## Position
0
## Min Cardinality
1
## Max Cardinality
1
## In Data Structure
> initially a data field must have at least one place it is part of and can update

TBDF-Incoming Weekly Measurement Data

## Data Class 
## Glossary Term
GlossaryTerm::ClinicalTrialTerminology::PatientId
## Namespace
> forms part of qualified name
## Version

## In Data Dictionary
Clinical Trial Data Dictionary

## Qualified Name

DataField::PatientId

___

#  foo Create Data Field
## Name
HospitalId
## Description
Unique identifier for a hospital
## Data Type
String
## Position
0
## Min Cardinality
1
## Max Cardinality
1
## Parent Data Field
DataField::PatientId
## In Data Structure
> initially a data field must have at least one place it is part of and can update

TBDF-Incoming Weekly Measurement Data

## Data Class 
## Glossary Term
GlossaryTerm::ClinicalTrialTerminology::PatientId
## Namespace
> forms part of qualified name
## Version

## In Data Dictionary
Clinical Trial Data Dictionary

## Qualified Name

DataField::HospitalId