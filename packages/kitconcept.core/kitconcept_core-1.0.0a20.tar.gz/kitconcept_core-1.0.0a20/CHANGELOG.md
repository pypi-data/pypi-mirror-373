# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 1.0.0a20 (2025-09-03)


### New features:

- Update core to Plone 6.1.2 @sneridagh [#39](https://github.com/kitconcept/kitconcept-core/issues/39)
- Move from `preview_image_link` to `kitconcept.core.person_image` attribute-based field. @sneridagh [#40](https://github.com/kitconcept/kitconcept-core/issues/40)


### Internal:

- Due to a problem with the last release, re-releasing. @sneridagh 

## 1.0.0a19 (2025-09-03)


### New features:

- Update core to Plone 6.1.2 @sneridagh [#39](https://github.com/kitconcept/kitconcept-core/issues/39)
- Move from `preview_image_link` to `kitconcept.core.person_image` attribute-based field. @sneridagh [#40](https://github.com/kitconcept/kitconcept-core/issues/40)

## 1.0.0a18 (2025-09-01)


### Bug fixes:

- Several VLT bugfixes. Update to VLT 7a25. @sneridagh 

## 1.0.0a17 (2025-08-26)


### Bug fixes:

- Fixed person images for search block. Update to VLT 7a24. @sneridagh 

## 1.0.0a16 (2025-08-25)


### New features:

- Update to Volto 18.24.0 and VLT 7a23. @sneridagh [#36](https://github.com/kitconcept/kitconcept-core/issues/36)

## 1.0.0a15 (2025-07-25)


### Internal:

- Update to VLT 7a19 @sneridagh 

## 1.0.0a14 (2025-07-23)

No significant changes.


## 1.0.0a13 (2025-07-17)


### Internal:

- Update VLT 7a15. @sneridagh 

## 1.0.0a12 (2025-07-10)


### Internal:

- Added new event calendar block.
  Added `footer_main_logo_inversed` image field to kitconcept.footer behavior, and related frontend code.
  Several fixes.
  Update to VLT 7a14. @sneridagh 

## 1.0.0a11 (2025-06-18)


### Bug fixes:

- Update to use VLT 7a13. @sneridagh 

## 1.0.0a10 (2025-06-18)


### Internal:

- Update to VLT 7a12. @sneridagh 

## 1.0.0a9 (2025-06-13)


### Bug fixes:

- Bring back Barceloneta Theme to ClassicUI. @sneridagh 


### Internal:

- Update Volto 18.23.0 and VLT 7a11. @sneridagh 

## 1.0.0a8 (2025-06-10)


### Internal:

- Update to VLT 7a10. Fixes CSS styling Person Teaser top. @sneridagh 

## 1.0.0a7 (2025-06-09)


### Internal:

- Update to VLT 7a9. @sneridagh 

## 1.0.0a6 (2025-06-06)


### Breaking changes:

- Use VLT 7a6. @sneridagh 


### Internal:

- Improved tests checking the position of the behavior. @sneridagh 
- Use VLT 7a8. @sneridagh 

## 1.0.0a5 (2025-05-23)


### New features:

- Added c.person as dependency, move person related things from k.intranet. @sneridagh [#13](https://github.com/kitconcept/kitconcept-core/issues/13)


### Internal:

- Update to VLT 6.1.0. @sneridagh 

## 1.0.0a4 (2025-05-16)


### Bug fixes:

- Fix migration tool exception access without a site hook being set. @ericof [#11](https://github.com/kitconcept/kitconcept-core/issues/11)

## 1.0.0a3 (2025-05-15)


### Internal:

- Explicitly add all content types to our generic setup profile. @sneridagh 
- Refactor site creation function to use three distinct profiles: base, cmfdependencies and dependencies. The later one is responsible for installing, on first run, the add-on dependencies for kitconcept.core. @ericof 
- Upgrade kitconcept.voltolighttheme to version 6.0.1 @sneridagh 
- Upgrade plone.volto to version 5.1.0 @ericof 


### Tests

- Add FTI tests for all content types. @ericof 
- Create a testing distribution to be used in internal tests. @ericof 

## 1.0.0a2 (2025-05-13)


### New features:

- Upgrade plone.restapi to version 9.14.0 @ericof [#6](https://github.com/kitconcept/kitconcept-core/issues/6)


### Internal:

- Remove old portlets registration -- but keep portlet managers (as they are required by other packages). @ericof [#3](https://github.com/kitconcept/kitconcept-core/issues/3)
- Pin Python to version 3.12 in pyproject.toml. @ericof [#4](https://github.com/kitconcept/kitconcept-core/issues/4)

## 1.0.0a1 (2025-05-09)


### New features:

- Add collective.volto.formsupport / collective.honeypot as dependencies. @ericof 
- Add kitconcept.voltolighttheme as dependency. @ericof 
- Add plonegovbr.socialmedia as dependency. @ericof
