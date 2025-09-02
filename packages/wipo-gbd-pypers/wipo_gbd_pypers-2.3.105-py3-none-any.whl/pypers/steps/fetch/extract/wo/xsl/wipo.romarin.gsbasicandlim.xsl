
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
	
<!-- ======================================================================================================== -->
	<!-- Changes
	 18/03/2014 Roger Holberton  Add ClassificationVersion (implemented 26/1/2015)
	 09/11/2015 Roger Holberton  Ignore NICCLAI=99
	 23/11/2017 Roger Holberton  Ignore FUN/LIMGR
	 -->
	<xsl:template match="BASICGS">
		<xsl:element name="GoodsServicesDetails"> 
			<xsl:element name="GoodsServices">
				<xsl:if test="@NICEVER">
					<xsl:element name="ClassificationVersion">
						<xsl:value-of select="@NICEVER"/>
					</xsl:element>
				</xsl:if>
				<xsl:apply-templates select="GSHEADEN|GSHEADFR|GSHEADES"/>
				<xsl:element name="ClassDescriptionDetails">
					<xsl:apply-templates select="GSGR"/>
				</xsl:element>
				<xsl:apply-templates select="GSFOOTEN|GSFOOTFR|GSFOOTES"/>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	<!-- ======================================================================================================== -->
	<xsl:template match="LIMGR|PRF|UPRF">
		<xsl:call-template name="makeGoodsServicesLimitation"/>
	</xsl:template>
	<xsl:template name="makeGoodsServicesLimitation">
		<xsl:element name="GoodsServicesLimitation">
			<xsl:variable name="cpcd" select="./DCPCD"/>
			<xsl:if test="$cpcd!=''">
				<xsl:element name="LimitationCountryDetails">
					<xsl:apply-templates select="./DCPCD" mode="limitation"/>
				</xsl:element>
			</xsl:if>
			<xsl:apply-templates select="./GSHEADEN|./GSHEADFR|./GSHEADES"/>
			<xsl:if test="./LIMTO|./REMVD|./ULIMTO|./UREMVD">
				<xsl:element name="LimitationClassDescriptionDetails">
					<xsl:apply-templates select="./LIMTO|./REMVD|./ULIMTO|./UREMVD"/>
				</xsl:element>
			</xsl:if>
			<xsl:apply-templates select="./GSFOOTEN|./GSFOOTFR|./GSFOOTES"/>
		</xsl:element>
	</xsl:template>
	
	
<xsl:template match="LIMTO|REMVD|ULIMTO|UREMVD|GSGR">
	<xsl:if test="@NICCLAI!='99'">
		<xsl:element name="ClassDescription">
			<xsl:apply-templates select="@NICCLAI"/>
			<xsl:apply-templates select="GSTERMEN|GSTERMFR|GSTERMES"/>
			<xsl:if test="name()='LIMTO' or name()='REMVD'">
				<xsl:element name="ClassLimitationCode">
					<xsl:choose>
						<xsl:when test="contains (name(),'LIMTO')">List limited to</xsl:when>
						<xsl:when test="contains (name(),'REMVD')">Remove from list</xsl:when>
					</xsl:choose>
				</xsl:element> 
			</xsl:if> 
		</xsl:element>
	</xsl:if>
</xsl:template>
	<!-- ======================================================================================================== -->
	<!-- -->
	<xsl:template match="@NICCLAI">
		<xsl:element name="ClassNumber">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="GSTERMEN|GSTERMFR|GSTERMES">
		<xsl:element name="GoodsServicesDescription">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="GSHEADEN|GSHEADFR|GSHEADES">
		<xsl:element name="GoodsServicesHeader">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="GSFOOTEN|GSFOOTFR|GSFOOTES">
		<xsl:element name="GoodsServicesFooter">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	
<xsl:template match="FUN/LIMGR"/>
	
</xsl:stylesheet>
