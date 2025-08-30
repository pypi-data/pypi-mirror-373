# mcp-pandoc Roadmap

*Strategic development roadmap for completing Pandoc's full potential within the MCP ecosystem*

## Overview

This roadmap focuses on leveraging Pandoc's native capabilities to make mcp-pandoc the definitive Pandoc MCP server. Following our "iPhone approach" philosophy, features are prioritized based on user impact, technical feasibility, and alignment with Pandoc's core strengths.

## Priority Matrix

| Priority | Feature | Use Cases | Pandoc-Native | Complexity |
|----------|---------|-----------|---------------|-----------|
| **P0 (Critical)** | Citation & Bibliography Management | Academic papers, research documents | ✅ Yes | Medium |
| **P1 (High)** | Math Equation Processing | Scientific docs, educational content | ✅ Yes | Low |
| **P1 (High)** | Cross-Reference System | Professional reports, books | ✅ Yes | Medium |
| **P2 (Medium)** | Custom Template Support | Branded documents, corporate styling | ✅ Yes | Medium |
| **P2 (Medium)** | Enhanced Filter Documentation | Improved filter ecosystem support | ✅ Yes | Low |
| **P3 (Future)** | Lua Filter Integration | Advanced document processing | ✅ Yes | Medium |

## Detailed Feature Breakdown

### P0 Features (Critical Priority)

#### 📚 Citation & Bibliography Management
**User Problem**: No academic/research document support
**Solution**: Leverage Pandoc's built-in citeproc capabilities
```yaml
Technical Approach:
- Add bibliography_file parameter to convert-contents tool
- Support BibTeX, BibLaTeX, CSL JSON/YAML formats
- Integrate CSL citation styles (APA, MLA, Chicago, etc.)
- Enable in-text citations and automatic bibliography generation

Dependencies:
- Pandoc citeproc (already built-in)
- No external dependencies required

Breaking Changes: None (additive parameters)
User Benefit: Professional academic document generation
Complexity: Medium (parameter handling, CSL integration)
```

### P1 Features (High Priority)

#### 🔢 Math Equation Processing
**User Problem**: Mathematical content not properly converted across formats
**Solution**: Enhanced LaTeX math support with format-specific optimization
```yaml
Technical Approach:
- Detect LaTeX math blocks (inline and display)
- Format-specific math rendering (MathML for HTML, native for LaTeX)
- Math-to-image conversion for formats without native support
- Preserve equation numbering and cross-references

Dependencies:
- Native Pandoc math processing
- LaTeX for PDF generation (already required)

Breaking Changes: None
User Benefit: Scientific and educational document support
Complexity: Low (native Pandoc capability)
```

#### 🔗 Cross-Reference System
**User Problem**: No way to reference figures, tables, equations by number
**Solution**: Implement pandoc-crossref functionality
```yaml
Technical Approach:
- Auto-numbering for figures, tables, equations, sections
- Cross-reference syntax (@fig:label, @tbl:label, @eq:label)
- Format-specific reference rendering
- Link generation for supported formats

Dependencies:
- pandoc-crossref filter (community standard)
- Enhanced metadata processing

Breaking Changes: None
User Benefit: Professional document structure and navigation
Complexity: Medium (filter integration, numbering logic)
```

### P2 Features (Medium Priority)

#### 🎨 Custom Template Support
**User Problem**: Generic document styling, no branding options
**Solution**: Pandoc template system integration
```yaml
Technical Approach:
- Add template_file parameter for custom templates
- Support LaTeX, HTML, DOCX templates
- Template validation and error handling
- Default template library for common use cases

Dependencies:
- Template validation utilities
- Example template collection

Breaking Changes: None (optional parameter)
User Benefit: Branded, professional document output
Complexity: Medium (template validation, format support)
```

#### 📖 Enhanced Filter Documentation
**User Problem**: Complex filter setup and environment management (addressing dipseth's feedback)
**Solution**: Comprehensive filter ecosystem support without native implementation
```yaml
Technical Approach:
- Create curated filter library in demo/filters/ directory
- Provide automated filter environment setup scripts
- Document best practices for filter dependencies
- Include troubleshooting guides for common issues

Dependencies:
- Documentation and examples only
- No additional code dependencies

Breaking Changes: None
User Benefit: Easier filter adoption, reduced setup complexity
Complexity: Low (documentation and examples)
```

### P3 Features (Future Development)

#### ⚙️ Lua Filter Integration
**User Problem**: Advanced document processing customization
**Solution**: Enable custom Lua filters for power users
```yaml
Technical Approach:
- Add lua_filters parameter (array of filter paths)
- Pre-validate filter syntax and dependencies
- Community filter integration (pandoc/lua-filters repo)
- Error handling and filter debugging

Dependencies:
- Native Pandoc Lua filter support
- Community filter library

Breaking Changes: None (optional parameter)
User Benefit: Unlimited document processing customization
Complexity: Medium (filter validation, error handling)
```

**Note**: Features requiring external tools (Mermaid, PlantUML, multi-document processing) are intentionally excluded to maintain focus on Pandoc-native capabilities and avoid maintenance complexity.

## Implementation Strategy

**Academic & Research Foundation**
**Focus**: Essential academic document capabilities
- Citation & bibliography management (native citeproc)
- Expands user base to academic and research communities
- Leverages Pandoc's strongest differentiating feature

**Scientific & Professional Enhancement**
**Focus**: Mathematical content and document structure
- Math equation processing (native Pandoc capability)
- Cross-referencing system for professional documents
- Enhanced user experience for complex documents

**Customization & Ecosystem Support**
**Focus**: Professional branding and filter support
- Custom template system for branded output
- Enhanced filter documentation and setup guides
- Complete Pandoc feature coverage

**Advanced Capabilities**
**Focus**: Power user features
- Lua filter integration for advanced customization
- Community-driven enhancements
- Ecosystem maturity and stability

## Success Metrics

### User Adoption Metrics
- **Filter Usage**: % of conversions using Pandoc filters
- **Academic Adoption**: Citation feature usage growth
- **Format Diversity**: Distribution of output formats used
- **Community Engagement**: GitHub stars, issues, contributions

### Technical Quality Metrics
- **Conversion Success Rate**: % of successful conversions
- **Performance**: Average conversion time by format
- **Error Rate**: Failed conversions per 1000 attempts
- **Test Coverage**: % code coverage for new features

### Ecosystem Impact Metrics
- **MCP Directory Ranking**: Position in MCP server listings
- **Integration Adoption**: Usage with popular MCP clients
- **Documentation Quality**: User documentation completeness
- **Community Contributions**: External filter/template contributions

## Risk Assessment

### Medium Risk
- **Citation Integration Complexity**: CSL and bibliography processing
- **Template System Scope**: Balancing flexibility vs. complexity
- **Cross-Reference Compatibility**: Support across all output formats

### Low Risk
- **Math Processing**: Well-established Pandoc capability
- **Filter Documentation**: No code implementation required
- **Template Support**: Native Pandoc feature
- **Lua Filter Integration**: Native Pandoc feature

### Eliminated Risks
- **External Dependencies**: No Node.js, Java, or other external tools required
- **Maintenance Burden**: Focused scope reduces complexity
- **Performance Impact**: No diagram generation or external process calls

## Dependencies & Prerequisites

### Required System Dependencies
```bash
# Current (unchanged)
pandoc >= 2.19.2
python >= 3.9
uv package manager

# Optional (already recommended)
texlive                   # For PDF generation
```

### Python Dependencies
```toml
# Minimal new dependencies
[dependencies]
requests = "^2.31.0"      # For CSL style downloads (citations)
# No additional dependencies for core features
```

## Migration Strategy

### Backward Compatibility Promise
- All existing parameters and functionality preserved
- New features added as optional parameters only
- Deprecation warnings for any future breaking changes
- Migration guides for major version upgrades

### API Evolution
```python
# Current convert-contents tool
{
  "input_format": "markdown",
  "output_format": "docx", 
  "content": "...",
  "output_file": "output.docx",
  "reference_doc": "template.docx"
}

# Enhanced tool with citation support (backward compatible)
{
  "input_format": "markdown",
  "output_format": "docx",
  "content": "...",
  "output_file": "output.docx", 
  "reference_doc": "template.docx",
  "bibliography_file": "refs.bib",    # NEW
  "citation_style": "apa"             # NEW
}
```

## Community & Ecosystem Strategy

### Documentation Strategy
- Feature-specific tutorials in README.md
- Workflow examples in CHEATSHEET.md
- Academic use case documentation
- Template and filter libraries

### Community Engagement
- Feature request prioritization via GitHub discussions
- Community filter/template contributions
- Integration examples with popular MCP clients
- Academic and professional user case studies

### Ecosystem Positioning
- **Primary**: Pandoc-native document conversion and processing
- **Secondary**: Academic and scientific publishing
- **Philosophy**: Focused excellence in document formats only

---

*This roadmap represents the focused evolution of mcp-pandoc as the definitive Pandoc MCP server, leveraging Pandoc's native capabilities while maintaining simplicity, reliability, and sustainable development practices. Features outside document conversion scope are intentionally excluded in favor of specialized servers.*