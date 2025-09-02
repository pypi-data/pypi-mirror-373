<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0">
<xsl:output method="xml"
            encoding="UTF-8"
            indent="no"/>
<xsl:variable name="tagnames-fileName" select="'ustm-tags.xml'"/>
<xsl:key name="tagName-lookup" match="tag" use="long"/>
<xsl:variable name="tagNames-top" select="document($tagnames-fileName)/tags"/>

<xsl:template name="getTagName">
<xsl:param name="tag"/>
<xsl:variable name="testTagText">
  <xsl:for-each select="$tagNames-top">
    <xsl:value-of select="key(&quot;tagName-lookup&quot;, $tag)/short"/>
  </xsl:for-each>
</xsl:variable>
<xsl:choose>
  <xsl:when test="string-length($testTagText) &gt; 0"><xsl:value-of select="$testTagText"/></xsl:when>
  <xsl:otherwise><xsl:value-of select="$tag"/></xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="case-file-header">
  <xsl:element name="head">
    <xsl:attribute name="flags">
      <xsl:call-template name="flags">
	<xsl:with-param name="content" select="."/>
      </xsl:call-template>
    </xsl:attribute>
    <xsl:apply-templates select="*"/>
  </xsl:element>
</xsl:template>
<!-- don't show any of this.  Just translate it into a bunch of flags in case we need it later -->
<xsl:template match="principal-register-amended-in|supplemental-register-amended-in|trademark-in|collective-trademark-in|service-mark-in|collective-service-mark-in|collective-membership-mark-in|certification-mark-in|cancellation-pending-in|published-concurrent-in|concurrent-use-in|concurrent-use-proceeding-in|interference-pending-in|opposition-pending-in|section-12c-in|section-2f-in|section-2f-in-part-in|renewal-filed-in|section-8-filed-in|section-8-partial-accept-in|section-8-accepted-in|section-15-acknowledged-in|section-15-filed-in|supplemental-register-in|foreign-priority-in|change-registration-in|intent-to-use-in|intent-to-use-current-in|filed-as-use-application-in|amended-to-use-application-in|use-application-currently-in|amended-to-itu-application-in|filing-basis-filed-as-44d-in|amended-to-44d-application-in|filing-basis-current-44d-in|filing-basis-filed-as-44e-in|filing-basis-current-44e-in|amended-to-44e-application-in|without-basis-currently-in|filing-current-no-basis-in|color-drawing-filed-in|color-drawing-current-in|drawing-3d-filed-in|drawing-3d-current-in|standard-characters-claimed-in|filing-basis-filed-as-66a-in|filing-basis-current-66a-in"/>

<xsl:template match="principal-register-amended-in|supplemental-register-amended-in|trademark-in|collective-trademark-in|service-mark-in|collective-service-mark-in|collective-membership-mark-in|certification-mark-in|cancellation-pending-in|published-concurrent-in|concurrent-use-in|concurrent-use-proceeding-in|interference-pending-in|opposition-pending-in|section-12c-in|section-2f-in|section-2f-in-part-in|renewal-filed-in|section-8-filed-in|section-8-partial-accept-in|section-8-accepted-in|section-15-acknowledged-in|section-15-filed-in|supplemental-register-in|foreign-priority-in|change-registration-in|intent-to-use-in|intent-to-use-current-in|filed-as-use-application-in|amended-to-use-application-in|use-application-currently-in|amended-to-itu-application-in|filing-basis-filed-as-44d-in|amended-to-44d-application-in|filing-basis-current-44d-in|filing-basis-filed-as-44e-in|filing-basis-current-44e-in|amended-to-44e-application-in|without-basis-currently-in|filing-current-no-basis-in|color-drawing-filed-in|color-drawing-current-in|drawing-3d-filed-in|drawing-3d-current-in|standard-characters-claimed-in|filing-basis-filed-as-66a-in|filing-basis-current-66a-in" mode="flag">
  <xsl:variable name="content">
    <xsl:call-template name="trim">
      <xsl:with-param name="content" select="."/>
    </xsl:call-template>
  </xsl:variable>
  <xsl:choose>
    <xsl:when test="(string-length($content) > 0) and ($content = 'T')">1</xsl:when>
    <xsl:otherwise>0</xsl:otherwise>
  </xsl:choose>
</xsl:template>

<!--
<xsl:template match="case-file|case-file-event-statement|case-file-event-statements|case-file-statements|case-file-statement|classifications|classification|correspondent|case-file-owners|case-file-owner|nationality|prior-registration-applications|prior-registration-application|international-registration|design-searches|design-search">
  <xsl:variable name="tagName">
    <xsl:call-template name="getTagName"><xsl:with-param name="tag" select="name()"/></xsl:call-template>
  </xsl:variable>
  <xsl:element name="{$tagName}">
    <xsl:apply-templates select="*"/>
  </xsl:element>
</xsl:template>
-->

<xsl:template match="@*">
  <xsl:apply-templates select="@*|node()"/>
</xsl:template>


<xsl:template match="*">
<xsl:variable name="tagName"><xsl:call-template name="getTagName"><xsl:with-param name="tag" select="name()"/></xsl:call-template></xsl:variable>
<xsl:element name="{$tagName}">
<xsl:apply-templates select="@*|node()"/>
</xsl:element>
</xsl:template>


<xsl:template name="trim">
	<xsl:param name="content"/>
	<xsl:call-template name="trim-right">
	<xsl:with-param name="content">
		<xsl:call-template name="trim-left">
		<xsl:with-param name="content" select="$content"/>
		</xsl:call-template>
	</xsl:with-param>
	</xsl:call-template>
</xsl:template>

<xsl:template name="trim-left">
	<xsl:param name="content"/>
	<xsl:choose>
	<xsl:when test="starts-with($content, '	') or starts-with($content, '
') or starts-with($content, ' ') or starts-with($content, '
')">
		<xsl:call-template name="trim-left">
			<xsl:with-param name="content" select="substring($content, 2)"/>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:value-of select="$content"/>
	</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<xsl:template name="trim-right">
	<xsl:param name="content"/>
	<xsl:variable name="length" select="string-length($content)"/>
	<xsl:variable name="last" select="substring($content, $length, 1)"/>
	<xsl:choose>
	<xsl:when test="($last = '	') or ($last = '
') or ($last = ' ') or ($last = '
')">
		<xsl:call-template name="trim-right">
		<xsl:with-param name="content" select="substring($content, 1, $length - 1)"/>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:value-of select="$content"/>
	</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<xsl:template name="flags">
  <xsl:apply-templates select="principal-register-amended-in" mode="flag"/><xsl:apply-templates select="supplemental-register-amended-in" mode="flag"/><xsl:apply-templates select="trademark-in" mode="flag"/><xsl:apply-templates select="collective-trademark-in" mode="flag"/><xsl:apply-templates select="service-mark-in" mode="flag"/><xsl:apply-templates select="collective-service-mark-in" mode="flag"/><xsl:apply-templates select="collective-membership-mark-in" mode="flag"/><xsl:apply-templates select="certification-mark-in" mode="flag"/><xsl:apply-templates select="cancellation-pending-in" mode="flag"/><xsl:apply-templates select="published-concurrent-in" mode="flag"/><xsl:apply-templates select="concurrent-use-in" mode="flag"/><xsl:apply-templates select="concurrent-use-proceeding-in" mode="flag"/><xsl:apply-templates select="interference-pending-in" mode="flag"/><xsl:apply-templates select="opposition-pending-in" mode="flag"/><xsl:apply-templates select="section-12c-in" mode="flag"/><xsl:apply-templates select="section-2f-in" mode="flag"/><xsl:apply-templates select="section-2f-in-part-in" mode="flag"/><xsl:apply-templates select="renewal-filed-in" mode="flag"/><xsl:apply-templates select="section-8-filed-in" mode="flag"/><xsl:apply-templates select="section-8-partial-accept-in" mode="flag"/><xsl:apply-templates select="section-8-accepted-in" mode="flag"/><xsl:apply-templates select="section-15-acknowledged-in" mode="flag"/><xsl:apply-templates select="section-15-filed-in" mode="flag"/><xsl:apply-templates select="supplemental-register-in" mode="flag"/><xsl:apply-templates select="foreign-priority-in" mode="flag"/><xsl:apply-templates select="change-registration-in" mode="flag"/><xsl:apply-templates select="intent-to-use-in" mode="flag"/><xsl:apply-templates select="intent-to-use-current-in" mode="flag"/><xsl:apply-templates select="filed-as-use-application-in" mode="flag"/><xsl:apply-templates select="amended-to-use-application-in" mode="flag"/><xsl:apply-templates select="use-application-currently-in" mode="flag"/><xsl:apply-templates select="amended-to-itu-application-in" mode="flag"/><xsl:apply-templates select="filing-basis-filed-as-44d-in" mode="flag"/><xsl:apply-templates select="amended-to-44d-application-in" mode="flag"/><xsl:apply-templates select="filing-basis-current-44d-in" mode="flag"/><xsl:apply-templates select="filing-basis-filed-as-44e-in" mode="flag"/><xsl:apply-templates select="filing-basis-current-44e-in" mode="flag"/><xsl:apply-templates select="amended-to-44e-application-in" mode="flag"/><xsl:apply-templates select="without-basis-currently-in" mode="flag"/><xsl:apply-templates select="filing-current-no-basis-in" mode="flag"/><xsl:apply-templates select="color-drawing-filed-in" mode="flag"/><xsl:apply-templates select="color-drawing-current-in" mode="flag"/><xsl:apply-templates select="drawing-3d-filed-in" mode="flag"/><xsl:apply-templates select="drawing-3d-current-in" mode="flag"/><xsl:apply-templates select="standard-characters-claimed-in" mode="flag"/><xsl:apply-templates select="filing-basis-filed-as-66a-in" mode="flag"/><xsl:apply-templates select="filing-basis-current-66a-in" mode="flag"/>
</xsl:template>

</xsl:stylesheet>
