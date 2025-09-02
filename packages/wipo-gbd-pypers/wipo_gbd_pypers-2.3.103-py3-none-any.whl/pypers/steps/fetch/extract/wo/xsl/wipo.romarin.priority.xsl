
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
<!-- ======================================================================================================== -->
	<xsl:template match="PRIGR">
		<xsl:element name="Priority">
			<xsl:apply-templates select="PRICP"/>
			<xsl:apply-templates select="PRIAPPN"/>
			<xsl:apply-templates select="PRIAPPD"/>
			<xsl:if test="PRIGS">
				<xsl:element name="PriorityPartialGoodsServices">
					<xsl:element name="ClassDescriptionDetails">
						<xsl:apply-templates select="PRIGS"/>
					</xsl:element> 
				</xsl:element>
			</xsl:if>
			<xsl:apply-templates select="TEXTEN|TEXTFR|TEXTES"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="PRICP">
		<xsl:element name="PriorityCountryCode">
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="PRIAPPN">
		<xsl:element name="PriorityNumber">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="PRIAPPD">
		<xsl:element name="PriorityDate">
			<xsl:value-of select='concat(substring(.,1,4),"-",substring(.,5,2),"-",substring(.,7,2))'/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="PRIGS">
		<xsl:element name="ClassDescription">
			<xsl:apply-templates select="@NICCLAI"/>
			<xsl:apply-templates select="GSTERMEN|GSTERMFR|GSTERMES"/> <!-- GSTERMEN|GSTERMFR|GSTERMES from  wipo.romarin.gsbasicandlim.xsl-->
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="TEXTEN|TEXTFR|TEXTES">
		<xsl:element name="Comment">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>	
	
	<!-- --> 

	

</xsl:stylesheet>
