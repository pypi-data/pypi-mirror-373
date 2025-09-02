<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
<!--
Changes
05/10/2011 Roger Holberton   Fix test of CLCN so license details are output
-->


	<xsl:template name="makeLicenseRecord">		
			<xsl:element name="MarkRecord">
				<xsl:element name="RecordLicence">
					<!-- -->
					<xsl:call-template name="makeRecordHeader">
						<xsl:with-param name="recordType">RecordLicenceKind</xsl:with-param>
					</xsl:call-template>
					
					<xsl:if test="@INTOFF">
						<xsl:element name="RecordInterrestedOfficeCode">
							<xsl:value-of select="@INTOFF"/>
						</xsl:element>
					</xsl:if>
					<!-- -->
					<xsl:if test="name()!='CLCN'">
						<xsl:element name="LicenceDetails">
						<!-- -->
							<xsl:element name="Licence">
								<xsl:element name="LicenceKind">
									<xsl:choose>
										<xsl:when test="@LICTYPE='EX'">
											<xsl:text>Exclusive License</xsl:text>
										</xsl:when>
										<xsl:when test="@LICTYPE='SO'">
											<xsl:text>Sole License</xsl:text>
										</xsl:when>
										<xsl:otherwise>
											<xsl:text>License</xsl:text>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:element>
								<!-- -->
								<xsl:element name="GoodsServicesLimitationIndicator">
									<xsl:choose>
										<xsl:when test="@ALLGSI='Y'">
											<xsl:text>false</xsl:text>
										</xsl:when>
										<xsl:otherwise>
											<xsl:text>true</xsl:text>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:element>
								<!-- -->
								<xsl:element name="TerritoryLimitationIndicator">
									<xsl:choose>
										<xsl:when test="@ALLOFF='Y'">
											<xsl:text>false</xsl:text>
										</xsl:when>
										<xsl:otherwise>
											<xsl:text>true</xsl:text>
										</xsl:otherwise>
									</xsl:choose>
								</xsl:element>
								<!-- -->
								<xsl:apply-templates select="GSCPSET"/>
								<!-- -->
								<xsl:apply-templates select="LICDURTN/DURTNEN|LICDURTN/DURTNFR|LICDURTN/DURTNES"/>  
								<!-- -->
								<xsl:element name="LicenseeDetails">
									<xsl:apply-templates select="LCSEEGR"/>
								</xsl:element>
								<!-- -->
								<xsl:if test="REPGR">
									<xsl:element name="RepresentativeDetails">
										<xsl:apply-templates select="REPGR" mode="details"/>
									</xsl:element>
								</xsl:if>
								<!-- -->
								<xsl:if test="PLCSEEGR">
									<xsl:element name="PreviousLicenseeDetails">
										<xsl:apply-templates select="PLCSEEGR"/>
									</xsl:element>
								</xsl:if>
								<!-- -->
							</xsl:element>
						</xsl:element>
					</xsl:if>
				</xsl:element>
			</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="GSCPSET">
		<xsl:element name="LicenseGoodsServicesCountriesSet">
			<xsl:element name="LicenseCountryDetails">
				<xsl:apply-templates select="LICDCPCD"/>
			</xsl:element>
			<xsl:apply-templates select="LIMTO|REMVD"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="LICDCPCD"> 
		<xsl:element name="LicenseCountry">
			<xsl:element name="LicenseCountryCode">
				<xsl:value-of select="DCPCD"/> 
			</xsl:element>
			<xsl:apply-templates select="TERRREEN|TERRREFR|TERRREES"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="TERRREEN|TERRREFR|TERRREES">
		<xsl:element name="TerritoryLimitationText">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/> </xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="DURTNEN|DURTNFR|DURTNES">
		<xsl:element name="PeriodLimitationText">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/> 
		</xsl:element>
	</xsl:template>
		<!-- ======================================================================================================== -->
</xsl:stylesheet>
