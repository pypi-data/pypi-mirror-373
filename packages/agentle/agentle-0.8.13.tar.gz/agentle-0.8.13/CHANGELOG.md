# Changelog

## v0.8.13
refactor(models): remove example fields from structured output models

Simplify model definitions by removing redundant example fields from Field descriptors

## v0.8.12
- refactor(models): remove examples from audio element description fields

The examples in the field definitions were removed to simplify the model and reduce maintenance overhead, as they were not essential to the core functionality and could be documented separately if needed.

## v0.8.11
- refactor(visual_media_description): remove example lists from field definitions

The example lists in field definitions were redundant as they were already covered in the description text. This change simplifies the model by removing duplicate information.

## v0.8.10

- refactor(whatsapp/models): replace dict types with specific message types

Use proper typed message classes instead of simplified dict structures to improve type safety and maintainability

## v0.8.9

- feat(agent): add method to update static knowledge
