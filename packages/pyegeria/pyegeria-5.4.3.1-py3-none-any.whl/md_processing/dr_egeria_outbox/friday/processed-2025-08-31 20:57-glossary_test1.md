# Don't List Glossaries
## Output Format
LIST
## Search String
*
## Page Size
100
____

# Don't List Terms
## Output Format
LIST
## Search String
Calico
## Page Size
5
## Starts With
True
## Ignore Case
True

____


# Don't Create Glossary

## Glossary Name

Dr.Egeria Test

## Language

English

## Description

This glossary is for testing Dr.Egeria

## Usage

Use Dr.Egeria commands to create elements.

## Version

1

## Qualified Name

Glossary::Dr.Egeria Test

___

Create a couple of categories for the glossary.


# Don't Create Folder

## Display Name

About Cats

## Description

This category is about cats

___
# Don't Add to Folder
## Member
About Cats
## Folder
Dr.Egeria Test
____

# Update Term

## Glossary

Glossary::Dr.Egeria Test

## Term Name

Calico

## Folders

About Cats

## Summary

Calico cats

## Description

Calico cats are common

## Abbreviation

## Examples

My calico cat is naughty

## Usage

As an adjective.

## Version

2

## Status

DRAFT

____

___

# Don't Add to Folder
## Member
Calico
## Folder
About Cats
___


## Reporting on Default Base Attributes - Perhaps couldn't find a valid combination of output_format_set and output_format?

# Update GlossaryTerm

## GlossaryTerm Name 

Siamese

## Display Name
Siamese

## Qualified Name
[Term::Siamese::3](#ecf8b8d6-e593-4240-839c-019b820f1897)

## Category
None

## Description
The Siamese cat is one of the first distinctly recognised breeds of Asian cat. It derives from the Wichianmat landrace.The Siamese cat is one of several varieties of cats native to Thailand. The original Siamese became one of the mostpopular breeds in Europe and North America in the 19th century

## GUID
ecf8b8d6-e593-4240-839c-019b820f1897

## Type Name
GlossaryTerm

## Metadata Collection Id
9905c3cb-94c5-4494-9229-0d6f69c0b842

## Metadata Collection Name
qs-metadata-store

## Version Identifier
None

## Classifications
[]

## Additional Properties
None

## Created By
erinoverview

## Create Time
2025-09-01T01:57:49.006+00:00

## Updated By
None

## Update Time
None

## Effective From
None

## Effective To
None

## Version
1

## Open Metadata Type Name
GlossaryTerm



# Don't Update Term

## Glossary Name

Glossary::Dr.Egeria Test

## Folder

About Cats

## Term Name

Persian

## Summary

A long hair cat

## Description

The Persian cat, also known as the Persian Longhair, is a long-haired breed of cat characterised by a round face and
short muzzle. The first documented ancestors of Persian cats might have been imported into Italy from Khorasan as early
as around 1620, but this has not been proven.

## Version

4

## Status

DRAFT

___

Now lets update the glossary we are just creating with an updated description.


# Don't Update Glossary

## Glossary Name

Dr.Egeria Test

## Language

English

## Description

This glossary is for testing Dr.Egeria

## Usage

Use Dr.Egeria commands to create elements. We'll start by creating categories for cats and dogs.

## Version

1.1

## Qualified Name

Glossary::Dr.Egeria Test

___

Create and fill out a category for dogs


#  Don't Create Folder

## Folder Name

About Dogs

## Description

This category is about dogs

____
# DOn't Add to Folder
## Member
About Dogs
## Folder
Glossary::Dr.Egeria Test

____


# Don't Update Term

## Glossary Name

Glossary::Dr.Egeria Test
## Categories
About Dogs
## Term Name

Labrador Retriever

## Summary

Labs are perhaps the most popular dog in the US.

## Description

The Labrador Retriever or simply Labrador is a British breed of retriever gun dog. It was developed in the United
Kingdom from St. John's water dogs imported from the colony of Newfoundland (now a province of Canada), and was named
after the Labrador region of that colony. It is among the most commonly kept dogs in several countries, particularly in
the Western world.

The Labrador is friendly, energetic, and playful.
It was bred as a sporting and hunting dog but is widely kept as a companion dog. It may also be trained as a guide or
assistance dog, or for rescue or therapy work.

## Abbreviation

Labs

## Examples

Leia was a mixed breed Lab

## Usage

A kind of dog

## Version

2

## Status

DRAFT


___

# Don't Create Term

## Glossary Name

Glossary::Dr.Egeria Test

## Term Name

Golden Retriever
## Glossary Category
Category::About Dogs
## Summary

Golden Retrievers are very popular dogs.

## Description

The Golden Retriever is a Scottish breed of retriever dog of medium size. It is characterised by a gentle and
affectionate nature and a striking golden coat. It is a working dog, and registration is subject to successful
completion of a working trial.[2] It is commonly kept as a pet and is among the most frequently registered breeds in
several Western countries; some may compete in dog shows or obedience trials, or work as a guide dog.

The Golden Retriever was bred by Sir Dudley Marjoribanks at his Scottish estate Guisachan in the late nineteenth
century. He cross-bred Flat-coated Retrievers with Tweed Water Spaniels, with some further infusions of Red Setter,
Labrador Retriever and Bloodhound. It was recognised by the Kennel Club in 1913, and during the interwar period spread
to many parts of the world.

## Version

3

## Status

DRAFT

___

# Don't Create Term

## Glossary Name

Glossary::Dr.Egeria Test

## Term Name

Terrier

## Summary

A vermin hunter

## Description

Terrier (from Latin terra, 'earth') is a type of dog originally bred to hunt vermin. A terrier is a dog of any one of
many breeds or landraces of the terrier type, which are typically small, wiry, game, and fearless. There are five
different groups of terrier, with each group having different shapes and sizes.

## Version

4

## Status

DRAFT

___


# Provenance

* Results from processing file glossary_test1.md on 2025-08-31 20:57
