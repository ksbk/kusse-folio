# Admin Fields

This file is a table-first reference for the current admin surfaces. It documents actual implemented fields, what they change on the live site, and any important constraints or hidden dependencies.

## Admin Surface Summary

| Admin model | Add/edit rule | Main use |
| --- | --- | --- |
| `Site Settings` | Singleton; only one record exists | Global brand, contact, metadata, and homepage controls |
| `Brand Settings` | Singleton; only one record exists | Visual brand controls: logo treatment, typography, color, shape, and social rendering mode |
| `About Profile` | Singleton; only one record exists | About page identity, content, portrait, and professional profile |
| `Social Link` | Multiple records | Structured footer/social links with optional icon support |
| `Service` | Multiple records | Services page content and ordering |
| `Project` | Multiple records | Project list/detail content, homepage featured pool, and project SEO |
| `Project Image` | Inline on `Project` | Project gallery and drawing/media structure |
| `Testimonial` | Inline on `Project`, also standalone admin | Client quotes on project detail pages and, when unlinked, the optional homepage testimonials section |
| `Contact Inquiry` | Read-only inbound records; add disabled | Enquiry workflow tracking only |

## Site Settings

### Identity

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `site_name` | Practice name in homepage hero, page title fallback, footer, and brand accessibility label | Max length `120`. Blank triggers an admin warning. Shorter names fit the homepage hero better. |
| `portfolio_preset` | Reusable homepage and navigation emphasis | `generic` keeps projects-first behavior. `academic` prioritizes Research and Publications when those modules are enabled. |
| `tagline` | Homepage subtitle and footer tagline | Max length `220`. Omitted from the hero/footer when blank. |
| `hero_label` | Small label above the homepage hero title | Max length `60`. Omitted when blank. |
| `hero_compact` | Switches the homepage hero into the compact title scale | Boolean. Use when long name/tagline makes the hero crowded. |
| `nav_name` | Overrides automatic navbar brand text | Max length `30`. If blank, navbar falls back to logo or automatic full-text/monogram logic. |
| `logo` | Replaces all text-based navbar branding | If present, it supersedes `nav_name`, full text, and monogram. Upload an export-sized asset that stays crisp without being oversized. |
| `og_image` | Default share image for pages without a page-specific image | Used for OG/Twitter fallback after any page override. Use a branded landscape image around `1200×630`; the current site serves this asset directly. |

### Contact

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `contact_email` | Public email shown in footer, contact page, and, when the portrait column is visible, the About portrait CTA area | Separate from the inbox that receives contact-form notifications. That inbox is `CONTACT_EMAIL` in the environment. Public contact details can be present while internal notification delivery is still unconfigured. |
| `phone` | Public phone number on the contact page | Omitted when blank. |
| `location` | Public studio/location text in footer, contact page, and About professional profile gate | Omitted when blank. Also required for the About professional profile block to render. |
| `address` | Stored in admin only right now | No public template surface currently reads it. |
| `contact_response_time` | Public response-time wording on the Contact page and success state | Defaults to `two working days`. Use short human-readable wording such as `24 hours` or `one week`. |

### Social

These inline URL fields are the quick setup path. They are useful when you only need
simple text links in the footer and contact page.

If you want icon-based social rendering, use `Social Link` records instead. The footer
prefers active `Social Link` entries over these inline fields when they exist.

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `linkedin_url` | LinkedIn link in footer and contact page | Omitted when blank. |
| `instagram_url` | Instagram link in footer and contact page | Omitted when blank. |
| `facebook_url` | Facebook link in footer | Omitted when blank. Not shown on the contact page. |
| `behance_url` | Behance link in footer and contact page | Omitted when blank. |
| `issuu_url` | Issuu link in footer and contact page | Omitted when blank. |

### SEO And Analytics

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `meta_description` | Homepage meta description and fallback meta description for other pages | Max length `160`. |
| `about_meta_description` | About page meta description | Falls back to `meta_description` when blank. |
| `blog_meta_title` | Blog list page meta title | Falls back to `Blog` when blank. |
| `blog_meta_description` | Blog list page meta description | Falls back to `meta_description` when blank. Only readiness-checked when Blog is enabled. |
| `projects_meta_description` | Projects list page meta description | Falls back to `meta_description` when blank. |
| `services_meta_title` | Services page meta title | Falls back to `Services` when blank. |
| `services_meta_description` | Services page meta description | Falls back to `meta_description` when blank. Only readiness-checked when Services is enabled. |
| `research_meta_title` | Research page meta title | Falls back to `Research` when blank. |
| `research_meta_description` | Research page meta description | Falls back to `meta_description` when blank. Only readiness-checked when Research is enabled. |
| `publications_meta_title` | Publications page meta title | Falls back to `Publications` when blank. |
| `publications_meta_description` | Publications page meta description | Falls back to `meta_description` when blank. Only readiness-checked when Publications is enabled. |
| `resume_meta_title` | Resume / CV page meta title | Falls back to `Resume / CV` when blank. |
| `resume_meta_description` | Resume / CV page meta description | Falls back to `meta_description` when blank. Only readiness-checked when Resume / CV is enabled. |
| `contact_meta_description` | Contact page meta description | Falls back to `meta_description` when blank. |
| `google_analytics_id` | Loads GA4 tracking script in the base template | Max length `30`. Script is omitted when blank. |

### Homepage Featured Projects

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `homepage_closing_text` | Homepage closing invitation above the contact CTA | Short closing line shown at the bottom of the homepage. Keep it concise so the CTA still reads cleanly. |
| `homepage_projects_mobile_count` | Max homepage featured cards shown at `<=639px` | Must be between `1` and `6`, and cannot exceed tablet count. |
| `homepage_projects_tablet_count` | Max homepage featured cards shown at `640-959px` | Must be between `1` and `6`, and cannot exceed desktop count. |
| `homepage_projects_desktop_count` | Max homepage featured cards queried and shown at `>=960px` | Must be between `1` and `6`. Defaults to `6`. |

### Admin Safety Already Implemented

| Safeguard | Current behavior |
| --- | --- |
| Blank `site_name` warning | Admin warns before sharing/publishing. |
| Blank `contact_email` warning | Admin warns when the public email is missing from `Site Settings`. |
| Missing notification inbox warning | Admin warns when `CONTACT_EMAIL` is not configured, even if the public contact email is present. |
| Long `site_name` info | Admin advises adding `nav_name` or a logo when the name exceeds `30` characters and no mitigation is set. |
| Single-letter monogram warning | Admin warns when the automatic monogram would collapse to one letter and no override is set. |
| Launch readiness summary | `Site Settings` shows the current blockers and warnings from the shared content-readiness check directly in admin. |
| Homepage fallback warning | Launch readiness warns when no featured projects are selected and the homepage will fall back to ordered projects. |
| Homepage hero placeholder warning | Launch readiness warns when the current homepage hero source has no cover image, so the hero will use the placeholder background. |
| Contact notification readiness warning | Launch readiness warns when the internal notification inbox is not configured, even if the public contact page still looks complete. |

## Brand Settings

### Logo Assets

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `logo_display_mode` | Controls the wrapper/background treatment around the navbar logo | `auto` is the default. `safe_card` adds a padded card-style background for logos that need extra contrast. |
| `logo_max_width` | Desktop navbar logo width cap | Default `160`. Must stay between `80` and `300`. |
| `logo_max_width_mobile` | Mobile navbar logo width cap | Default `120`. Must be less than or equal to desktop width. |
| `logo_light` | Optional light-context logo asset | Falls back to the master `Site Settings.logo` when blank. |
| `logo_dark` | Optional dark-context logo asset | Falls back to the master logo when blank. |
| `logo_icon` | Optional square icon asset | Intended for icon/fav-style uses. Falls back to the master logo when blank. |

### Typography, Color, And Shape

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `typography_preset` | Sets the heading/body type pairing site-wide | Applied through CSS custom properties. |
| `color_preset` | Sets the accent color system | Named presets are bundled. Use `custom` to unlock `accent_color_custom`. |
| `accent_color_custom` | Sets a custom accent color | Must be a 6-digit hex color with a leading `#`, e.g. `#B45309`. |
| `visual_style` | Controls global corner rounding | Affects cards, buttons, and image treatments. |

### Social Links Display

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `social_links_display` | Controls how footer social links render | `text` works with simple labels. `icons` and `icons_text` require active `Social Link` entries with `icon_slug` populated. |

## Social Links

Use `Social Link` records when you want structured control over order, label, and icon-based
display. This is the recommended path when Brand Settings uses `icons` or `icons_text`.

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `label` | Public link label | Used as the visible text label and accessibility label. |
| `url` | Social destination | Public link target. |
| `icon_slug` | Optional icon key used by the footer renderer | Required for icon-based display modes. Examples: `linkedin`, `github`, `instagram`. |
| `order` | Footer ordering | Lower numbers appear first. |
| `active` | Public visibility | Only active links render. When any active `Social Link` exists, the footer prefers these entries over the legacy inline URL fields. |

## About Profile

### Identity

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `identity_mode` | Chooses whether the About hero introduces a person or the studio | `person` uses principal fields when present; `studio` uses the site/practice path. |
| `principal_name` | About hero title for person-led mode | Required in practice for person-led mode. Ignored on the public page for studio-led mode. |
| `principal_title` | About hero meta line in person-led mode | Combined with `site_name` when both exist. |
| `practice_structure` | Short studio descriptor under the About hero title | Hidden if still placeholder text or blank. |
| `one_line_practice_description` | About hero subtitle | Omitted when blank. |

### Content

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `practice_summary` | Opening About prose block | Omitted when blank. |
| `project_leadership` | Secondary About prose block | Hidden if still placeholder text or blank. |
| `approach` | About “Approach” section | Omitted when blank. |
| `closing_invitation` | About CTA copy near the bottom of the page | If `<= 80` characters, it becomes the CTA heading. If longer, the page uses the fixed heading “Have a project in mind?” and renders this field as supporting body text. |

### Professional Profile

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `professional_standing` | Professional Profile block item | Hidden if still placeholder text or blank. |
| `education` | Professional Profile list items | One line per item. |
| `supporting_facts` | Professional Profile list items | One line per item. Used as factual proof; not positioning copy. |
| `experience_years` | Professional Profile list item | Publicly rendered as `N+ years in practice`. |

### Files And Display

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `portrait_mode` | Controls whether the portrait column can render | `text_only` removes the portrait block entirely. No gray placeholder is shown publicly. |
| `portrait` | About portrait image | Only visible when `portrait_mode=portrait` and an image exists. |
| `cv_file` | Download button in the portrait column | Only visible when the portrait column is visible, so in practice it needs `portrait_mode=portrait` and a portrait image. |

### About Page Render Gates

| Gate | Current behavior |
| --- | --- |
| Portrait column | Renders only when `portrait_mode=portrait` and `portrait` exists. |
| Professional Profile block | Renders only when `site_settings.location`, public professional standing, `experience_years`, and at least one education/supporting-fact line are all present. |

## Services

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `name` | Service heading | Max length `120`. |
| `short_description` | Service summary text | Used on cards and homepage/service previews. |
| `long_description` | Extended service prose | Optional. Shown on the Services page below the summary when present. |
| `order` | Service ordering on the Services page | Lower numbers appear first. |
| `active` | Public visibility on the Services page | Only active services are listed publicly. |

## Projects

### Main Project Fields

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `title` | Project card title, detail-page title, breadcrumbs, and default slug source | Max length `200`. |
| `slug` | Project URL path | Prepopulated from title; must be unique. |
| `short_description` | Project card description, project hero description, and SEO fallback | Max length `300`. |
| `cover_image` | Project detail hero image, project OG image, and homepage hero image source for the first selected homepage project | If blank, the detail page falls back to the first gallery image for hero/share media when one exists; otherwise detail hero switches to the no-image layout. The homepage hero may still use the placeholder if this is the selected hero project and no cover image exists. Use an optimized landscape export because this file is also a likely LCP asset. |
| `tags` | Project list filtering, card metadata, detail-page label, and related-project matching | Comma-separated tags. The first tag is used as the visible label on cards and detail pages. |
| `status` | Project detail metadata row | Fixed choices: `Completed`, `In Progress`, `Concept`, `Competition Entry`. |
| `featured` | Eligibility for homepage featured-project selection | Homepage prefers featured projects first. |
| `order` | Ordering in homepage selection, project list, and related-project picking | Lower numbers appear first. |
| `location` | Card metadata and project detail metadata row | Omitted when blank. |
| `year` | Card metadata and project detail metadata row | Omitted when blank. |
| `client` | Project detail metadata row | Omitted when blank. |
| `area` | Project detail metadata row | Omitted when blank. |
| `services_provided` | Project detail metadata row | One line per service via `linebreaksbr`. |
| `overview` | “Overview” section | Omitted when blank. |
| `challenge` | “Challenge & Context” section | Omitted when blank. |
| `concept` | “Design Concept” section | Omitted when blank. |
| `process` | “Process” section | Omitted when blank. |
| `outcome` | “Outcome” section | Omitted when blank. |
| `seo_title` | Project page `<title>` override | Falls back to `title` when blank. |
| `seo_description` | Project page meta-description override | Falls back to `short_description` when blank. |

### Project Image Inline

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `image` | Public image asset | Required for each inline row. Upload an optimized export rather than a huge original; gallery and supporting images are served directly on the public site. |
| `image_type` | Determines whether the image appears in the gallery flow or in the detail page’s supporting-media section | `gallery` images feed the main gallery; all other types go to the shared supporting-media section. |
| `caption` | Figure caption | Used when present. Also used as alt fallback before project title if `alt_text` is blank. |
| `alt_text` | Image alt text | Falls back to `caption`, then project title if blank. |
| `order` | Image ordering within gallery/drawings | Lower numbers appear first. If `cover_image` is blank, the first gallery image by order becomes the detail hero/share fallback. |

### Testimonial Inline / Standalone

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `name` | Testimonial attribution | Public on project pages and, for standalone testimonials, on the homepage section. |
| `role` | Testimonial attribution meta | Public when present. |
| `company` | Testimonial attribution meta | Public when present. |
| `quote` | Testimonial body | Public on project pages and on the homepage when the testimonial is used as a standalone entry. |
| `order` | Testimonial ordering | Lower numbers appear first. |
| `active` | Public visibility | Inactive testimonials are hidden everywhere. |

### Testimonial Render Rules

| Rule | Current behavior |
| --- | --- |
| Project-linked testimonials | Active testimonials linked to a `Project` render on that project’s detail page. |
| Standalone testimonials | Active testimonials with no linked project may render on the homepage when `Site Settings.testimonials_enabled=True`. |
| Inactive testimonials | Hidden on both project detail pages and the homepage. |

## Contact Inquiries

| Field | Public effect | Constraints / notes |
| --- | --- | --- |
| `name` | None | Read-only in admin. Captured from the form. |
| `email` | None | Read-only in admin. Used for reply workflow. |
| `company` | None | Read-only in admin. |
| `project_type` | None | Read-only in admin. Prefilled from service enquiry links and from the project-detail CTA path. |
| `location` | None | Read-only in admin. |
| `budget_range` | None | Read-only in admin. |
| `timeline` | None | Read-only in admin. |
| `message` | None | Read-only in admin. |
| `created_at` | None | Read-only in admin. |
| `status` | Admin workflow only | Editable. Choices: `new`, `read`, `replied`, `archived`. |
| `notes` | Admin workflow only | Internal notes only; never shown to the client. |

### Contact Inquiry Admin Rules

| Rule | Current behavior |
| --- | --- |
| Add permission | Disabled. Inquiries are created by the public form only. |
| Public visibility | None. This model does not drive a public page. |
| Delivery fallback | A valid inquiry is still saved when notification email is unavailable or delivery fails. The public thank-you page switches to a saved-only confirmation state instead of pretending notification succeeded. |
