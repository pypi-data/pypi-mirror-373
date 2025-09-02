<xsl:stylesheet version="1.0"  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
	<!-- -->
	<!-- Force MarkVerbalElement to be present -->
	<!-- ======================================================================================================== -->
	<xsl:template match="MARDESGR">
		<xsl:element name="MarkDescriptionDetails">
			<xsl:apply-templates select="node()"/>
			<xsl:apply-templates select="../VOLDESGR/VOLDESEN|../VOLDESGR/VOLDESFR|../VOLDESGR/VOLDESES"/>
		</xsl:element>
	</xsl:template>
	<xsl:template match="VOLDESGR">
		<xsl:if test="not(../MARDESGR)"> 
			<xsl:element name="MarkDescriptionDetails">
				<xsl:apply-templates select="node()"/>
			</xsl:element>
		</xsl:if>
	</xsl:template>
	<xsl:template match="MARDESEN|MARDESFR|MARDESES">
		<xsl:element name="MarkDescription">
			<xsl:attribute name="languageCode"><xsl:value-of select="substring(name(),7,2)"/></xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<xsl:template match="VOLDESEN|VOLDESFR|VOLDESES">
		<xsl:element name="MarkVoluntaryDescription">
			<xsl:attribute name="languageCode"><xsl:value-of select="substring(name(),7,2)"/></xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="DISCLAIMGR">
		<xsl:element name="MarkDisclaimerDetails">
			<xsl:apply-templates select="node()"/>
		</xsl:element>
	</xsl:template>
	<xsl:template match="DISCLAIMEREN|DISCLAIMERFR|DISCLAIMERES">
		<xsl:element name="MarkDisclaimer">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template name="makeWordMarkSpecification">
		<xsl:element name="WordMarkSpecification">
			<xsl:apply-templates select="./IMAGE/@TEXT"/>
			<xsl:if test="not(./IMAGE/@TEXT)">
					<xsl:element name="MarkVerbalElementText"/>
			</xsl:if>
			<xsl:apply-templates select="./SIGVRBL"/>
			<xsl:element name="MarkVerbalElementSignificantIndicator">
				<xsl:choose>
					<xsl:when test="./VRBLNOT">
						<xsl:text>false</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:text>true</xsl:text>
					</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
			<xsl:apply-templates select="./MARTRGR"/>
			<xsl:apply-templates select="./MARTRAN"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="IMAGE/@TEXT">
		<xsl:element name="MarkVerbalElementText">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="MARTRGR">
		<xsl:apply-templates select="./MARTREN|./MARTRFR|./MARTRES"/>
	</xsl:template>
	<xsl:template match="MARTREN|MARTRFR|MARTRES">
		<xsl:element name="MarkTranslation">
			<xsl:attribute name="languageCode"><xsl:call-template name="makeLanguage"><xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param></xsl:call-template></xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="MARTRAN">
		<xsl:element name="MarkTransliteration">
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="IMAGE">
		<xsl:element name="MarkImageDetails">
			<xsl:element name="MarkImage">
				<xsl:element name="MarkImageFilename"><xsl:variable name="filename" select="@NAME"/><xsl:value-of select='concat("https://www.wipo.int/madrid/monitor/api/v1/image/WO50", format-number($filename,"000000000000"))'/></xsl:element>
				<!-- -->
				<xsl:element name="MarkImageFileFormat">
					<!-- really for the fun of it ......-->
					<xsl:variable name="lcjpg">jpg</xsl:variable>
					<xsl:variable name="ucjpg">JPG</xsl:variable>
					<xsl:variable name="filetype" select="@TYPE"/>
					<xsl:choose>
						<xsl:when test="translate($filetype,$lcjpg,$ucjpg)='JPG'">
							<!-- hin hin hin -->
							<xsl:text>JPEG</xsl:text>
						</xsl:when>
						<xsl:otherwise>
							<xsl:value-of select="@TYPE"/>
						</xsl:otherwise>
					</xsl:choose>
				</xsl:element>
				<!-- -->
				<xsl:choose>
					<xsl:when test="../MARCOLI">
						<xsl:element name="MarkImageColourIndicator">
							<xsl:text>true</xsl:text>
						</xsl:element>
					</xsl:when>
					<xsl:otherwise>
						<xsl:apply-templates select="@COLOUR"/>
					</xsl:otherwise>
				</xsl:choose>
				<!-- -->
				<xsl:apply-templates select="../COLCLAGR"/>
				<!-- -->
				<xsl:apply-templates select="../VIENNAGR"/>
				
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="COLCLAGR">
		<xsl:apply-templates select="COLCLAEN|COLCLAFR|COLCLAES"/>
		<xsl:apply-templates select="COLPAREN|COLPARFR|COLPARES"/>
	</xsl:template>
	<xsl:template match="COLCLAEN|COLCLAFR|COLCLAES">
		<xsl:element name="MarkImageColourClaimedText">
			<xsl:attribute name="languageCode"><xsl:call-template name="makeLanguage"><xsl:with-param name="lang"><xsl:value-of select=" name()"/></xsl:with-param></xsl:call-template></xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<xsl:template match="COLPAREN|COLPARFR|COLPARES">
		<xsl:element name="MarkImageColourPartClaimedText">
			<xsl:attribute name="languageCode"><xsl:call-template name="makeLanguage"><xsl:with-param name="lang"><xsl:value-of select=" name()"/></xsl:with-param></xsl:call-template></xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="VIENNAGR">
		<xsl:element name="MarkImageCategoryDetails">
			<xsl:if test="VIECLAI">
				<xsl:element name="MarkImageCategory">
					<xsl:element name="CategoryKind">
						<xsl:text>Vienna Two Levels</xsl:text>
					</xsl:element>
					<xsl:element name="CategoryCodeDetails">
					<xsl:apply-templates select="VIECLAI"/>
				</xsl:element>
				</xsl:element>
			</xsl:if> 
			<xsl:if test="VIECLA3">
				<xsl:element name="MarkImageCategory">
					<xsl:element name="CategoryKind">
						<xsl:text>Vienna Three Levels</xsl:text>
					</xsl:element>
					<xsl:element name="CategoryCodeDetails">
						<xsl:apply-templates select="VIECLA3"/>
					</xsl:element>
				</xsl:element>
			</xsl:if> 
		</xsl:element>
	</xsl:template>
	<xsl:template match="VIECLAI|VIECLA3">
		<xsl:element name="CategoryCode">
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="@COLOUR">
		<xsl:element name="MarkImageColourMode">
			<xsl:choose>
				<xsl:when test=".='Y'">
					<xsl:text>Colour</xsl:text>
				</xsl:when>
				<xsl:when test=".='N'">
					<xsl:text>Not Colour</xsl:text>
				</xsl:when>
				<xsl:when test=".='B'">
					<xsl:text>Black and White</xsl:text>
				</xsl:when> 
				<xsl:when test=".='G'"> 
					<xsl:text>Greyscale</xsl:text>
				</xsl:when>
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="SIGVRBL">
		<xsl:element name="MarkSignificantVerbalElement">
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
</xsl:stylesheet>
