---
title: pymdownx.blocks.details
summary: Collapsible details
external_links:
  Reference: https://facelessuser.github.io/pymdown-extensions/extensions/blocks/plugins/details/
---


The `pymdownx.blocks.details` extension is a Python-Markdown plugin that provides a simple way to create collapsible "details" blocks in your Markdown content. 

## Configuration

```yaml
# mkdocs.yml

markdown_extensions:
  - pymdownx.blocks.details
```

## Syntax

```md
### FAQ

/// details | Why copy/paste and not packaged as a dependency?
The idea behind this is to give you ownership and control over the code, allowing you to decide how the components are built and styled.

Start with some sensible defaults, then customize the components to your needs.

*One of the drawbacks of packaging the components in an npm package is that the style is coupled with the implementation. The design of your components should be separate from their implementation.*
///

/// details | Do you plan to publish it as an npm package?
No. I have no plans to publish it as an npm package.
///

/// details | Which frameworks are supported?
You can use any framework that supports React. Next.js, Astro, Remix, Gatsby etc.
///
```

### FAQ

/// details | Why copy/paste and not packaged as a dependency?
The idea behind this is to give you ownership and control over the code, allowing you to decide how the components are built and styled.

Start with some sensible defaults, then customize the components to your needs.

*One of the drawbacks of packaging the components in an npm package is that the style is coupled with the implementation. The design of your components should be separate from their implementation.*
///

/// details | Do you plan to publish it as an npm package?
No. I have no plans to publish it as an npm package.
///

/// details | Which frameworks are supported?
You can use any framework that supports React. Next.js, Astro, Remix, Gatsby etc.
///

