# Compliance checklist

Do each item on every page in scope. Record the result in the report.

## Accessibility (WCAG 2.2 AA)
- [ ] One h1 per page. Headings go in order with no skipped levels.
- [ ] Text contrast 4.5:1. Large text and UI parts 3:1. Measure each brand pair.
- [ ] Flag every contrast failure that the source also has (for example white on orange at 2.3:1). Ask the user: keep the source look or darken the color.
- [ ] Every image has alt text from the source or a short true description. Decorative images have empty alt.
- [ ] Icon-only links and buttons have an accessible name.
- [ ] All controls work with the keyboard. Focus is visible (3px outline or more).
- [ ] Touch targets are 24px or more (aim for 44px).
- [ ] Sliders: previous, next and dot buttons; `aria-roledescription`; `aria-live` polite; autoplay off by default or a pause; autoplay stops on hover and focus (WCAG 2.2.2).
- [ ] Motion stops under `prefers-reduced-motion: reduce`.
- [ ] Skip link is on. Menus open with Enter, Space and arrow keys, and close with Esc.
- [ ] Form fields have labels, required marks and clear error text.
- [ ] No horizontal scroll at 320px. Text can zoom to 200%.

## Semantic HTML
- [ ] Sections use `section`, `header`, `nav`, `main`, `footer`, `figure`, `blockquote`.
- [ ] Lists are `ul` or `ol`. Buttons are `button`. Links are `a`.
- [ ] Language is set on the page.

## SEO
- [ ] Title 60 characters or less, unique per page.
- [ ] Description 70 to 160 characters.
- [ ] Social image 1200px wide or more.
- [ ] Structured data (Organization, LocalBusiness or WebPage) with real facts only.
- [ ] Old URLs map to new URLs. List the redirects the user must set when the domain moves.
- [ ] No references to the old domain remain (linkcheck reports them).

## Privacy and consent
- [ ] The Peerfold consent banner is on.
- [ ] Analytics and tracking IDs go in `sites_set_tracking_ids`, not in module scripts, so consent mode controls them.
- [ ] Third-party embeds (maps, video) load only after consent where the platform supports it.
- [ ] A privacy policy link is in the footer. Use the source policy text. Do not write a new one.

## Function
- [ ] Every source form is mapped to a native form with the same fields. A test submit succeeds (ask before you submit on a live site).
- [ ] All internal links return 200. All anchors exist.
- [ ] Phone and email links use `tel:` and `mailto:`.
- [ ] Header CTA, nav, mobile drawer, sliders and video work at 1440 and 390.

## Performance
- [ ] Images are 2000px wide or less and compressed (JPEG quality about 85).
- [ ] Fonts load as woff2. Only the weights in use.
- [ ] Animated backgrounds pause when off screen and under reduced motion.
