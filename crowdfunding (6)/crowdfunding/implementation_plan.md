# UI Alignment & Styling Implementation Plan

The objective is to fix broken form and table alignments across the site while maintaining the existing premium "attractive" glassmorphism theme requested by the user.

## Proposed Changes

We will systematically review and modify the HTML templates, specifically targeting forms and tables that are misaligned. The changes rely purely on frontend HTML/CSS adjustments and will not alter database schemas or backend view logic.

### Global CSS/Structural Fixes
Instead of defining styles inline on every file, we will focus on applying consistent `div` container classes that use predefined modern UI CSS (or defining a unified block of `<style>` in a common header if required, but ideally using the `layout.css` where possible or injecting custom styling where it lacks).
*   **Forms**: Wrap inputs in consistent margins (`mb-3`, `form-group`), ensuring labels and inputs stack cleanly or align on a grid, applying a glassmorphism background to the form container.
*   **Tables**: Ensure `width: 100%`, `border-collapse: collapse`, and apply distinct padding with alternating row colors or hover effects to improve readability.

### Target Templates

*   **Authentication**:
    *   [login.html](file:///c:/Project/crowdfunding/template/login.html)
    *   [template/donor/donor_register.html](file:///c:/Project/crowdfunding/template/donor/donor_register.html)
*   **Hospital Module**:
    *   [template/Hospital/register_patient.html](file:///c:/Project/crowdfunding/template/Hospital/register_patient.html)
    *   [template/Hospital/view_patients.html](file:///c:/Project/crowdfunding/template/Hospital/view_patients.html)
    *   [template/Hospital/addHospital.html](file:///c:/Project/crowdfunding/template/Hospital/addHospital.html)
    *   [template/Hospital/RegisterExpense.html](file:///c:/Project/crowdfunding/template/Hospital/RegisterExpense.html)
*   **Admin Module**:
    *   [template/Admin/addCategory.html](file:///c:/Project/crowdfunding/template/Admin/addCategory.html)
    *   [template/Admin/viewCategory.html](file:///c:/Project/crowdfunding/template/Admin/viewCategory.html)
    *   [template/Admin/viewAllHospitalRequest.html](file:///c:/Project/crowdfunding/template/Admin/viewAllHospitalRequest.html)
    *   ... and other data view tables.

We will proceed directory by directory (Admin, Hospital, Donor) updating the `<table>` and `<form>` tags to use a beautiful, centered, and aligned layout.

## Verification
*   We will visually verify the templates to ensure everything is aligned correctly, typically centering forms with appropriate max-widths and making tables expand to container widths with readable padding.
