<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">


<xsl:template name="makeBasicRecord">
		
	<!-- -->
		<xsl:param name="basicRecordKind">xxx</xsl:param>	 
			<xsl:element name="MarkRecord">
				<xsl:element name="BasicRecord">
					<!-- -->
					<xsl:call-template name="makeRecordHeader">
						<xsl:with-param name="recordType">BasicRecordKind</xsl:with-param>
					</xsl:call-template>
					<!-- -->
					<xsl:apply-templates select="./FACTS/FACTSEN|./FACTS/FACTSFR|./FACTS/FACTSES|TEXTEN|TEXTES|TEXTFR" mode="record"/>
					<!-- -->	
					<xsl:if test="@INTOFF">
						<xsl:element name="RecordInterestedOfficeCode">
							<xsl:value-of select="@INTOFF"/>
						</xsl:element>
					</xsl:if>
					<!-- -->	
					<xsl:if test="./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD|./DCPCD and name()!='CBNP' and name()!='LIN' and name()!='PCN' ">
						<xsl:element name="RecordDesignatedCountryDetails">
							<xsl:apply-templates select="./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD"/>
							<xsl:apply-templates select="./DCPCD" mode="nonrenewal" />  <!-- For REN3 -->
 						</xsl:element>
					</xsl:if>
					<!-- -->
					<xsl:if test="./INTENTG">
						<xsl:element name="RecordUseIntentDetails">
							<xsl:apply-templates select="./INTENTG/CPCD"/>
						</xsl:element>
					</xsl:if>		
					<!-- -->				
					<xsl:if test="./LIMGR|./PRF|./UPRF">
						<xsl:element name="GoodsServicesLimitationDetails">
							<xsl:apply-templates select="./LIMGR|./PRF|./UPRF"/>
						</xsl:element>
					</xsl:if>
							
					<!-- -->		
					<xsl:if test="name()='CBNP' or name()='LIN' or name()='PCN' or name()='LNN'">
						<xsl:element name="GoodsServicesLimitationDetails">
							<xsl:call-template name="makeGoodsServicesLimitation"/>
						</xsl:element>
					</xsl:if>
					<!-- -->
					<xsl:if test="./SENGRP">
						<xsl:call-template name="makeSeniority"/>
					</xsl:if>
					<!-- -->
					<xsl:if test="./BASGR">
						<xsl:element name="BasicRegistrationApplicationDetails">
							<xsl:apply-templates select="./BASGR"/>
						</xsl:element>
					</xsl:if>
					<!-- -->
				</xsl:element>
			</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="FACTSEN|FACTSFR|FACTSES|TEXTEN|TEXTFR|TEXTES" mode="record">
		<xsl:element name="FactDecisionText">
			<xsl:attribute name="languageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select=" name()"/></xsl:with-param>
				</xsl:call-template>
			</xsl:attribute>
			<xsl:value-of select="text()"/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="CPCD">
		<xsl:element name="RecordUseIntentCountryCode">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->

	

</xsl:stylesheet>
