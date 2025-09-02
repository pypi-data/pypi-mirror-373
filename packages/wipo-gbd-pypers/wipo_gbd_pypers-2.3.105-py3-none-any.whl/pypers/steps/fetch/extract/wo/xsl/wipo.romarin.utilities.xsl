
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
<!-- ======================================================================================================== -->
	<xsl:template name="makeLanguage">
		<xsl:param name="lang">xxx</xsl:param>
		 <xsl:variable name="langcode" select="concat($lang,'end')"/>
		 <xsl:choose>			 
			<xsl:when test="$lang='1' or contains($langcode,'ENend')">
				<xsl:text>en</xsl:text> 
			</xsl:when>
			<xsl:when test="$lang='3' or contains($langcode,'FRend')">
				 <xsl:text>fr</xsl:text>
			</xsl:when>
			<xsl:when test="$lang='4' or contains($langcode,'ESend')">
				<xsl:text>es</xsl:text>
			</xsl:when>
			<xsl:otherwise>
				<xsl:text>xx</xsl:text>
			</xsl:otherwise>
		</xsl:choose> 
</xsl:template>

	

</xsl:stylesheet>
