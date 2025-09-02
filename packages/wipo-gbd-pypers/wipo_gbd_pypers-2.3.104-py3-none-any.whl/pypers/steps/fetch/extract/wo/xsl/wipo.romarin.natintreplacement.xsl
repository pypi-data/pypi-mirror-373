<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
 
	<xsl:template name="makeNatIntReplacement">
		<!-- -->			
		<xsl:element name="MarkRecord">
			<xsl:element name="RecordNationalInternationalReplacement">
				<!-- -->
				<xsl:call-template name="makeRecordHeader">
					<xsl:with-param name="recordType">skip</xsl:with-param>
				</xsl:call-template>
				<!-- -->	
				<xsl:if test="@INTOFF">
					<xsl:element name="RecordInterestedOfficeCode">
						<xsl:value-of select="@INTOFF"/>
					</xsl:element>
				</xsl:if>
								<!-- -->		
				<xsl:if test="GSHEADEN|GSHEADFR|GSHEADEN|LIMTO|REMVD|GSFOOTEN|GSFOOTFR|GSFOOTES">
					<xsl:call-template name="makeGoodsServicesLimitation"/>
				</xsl:if>
				<!-- -->		
				<xsl:element name="NationalMarkDetails">
					<xsl:apply-templates select="NATGR"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>	
	<!-- -->	
	<!-- ======================================================================================================== -->
	<xsl:template match="NATGR">
		<xsl:element name="NationalMark">
			<xsl:element name="NationalMarkRegistrationNumber">
				<xsl:value-of select="NATRNUM"/>
			</xsl:element>
			<xsl:if test="NATFDAT">
				<xsl:element name="NationalMarkFilingDate">
					<xsl:value-of select='concat(substring(NATFDAT,1,4),"-",substring(NATFDAT,5,2),"-",substring(NATFDAT,7,2))'/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="NATRDAT">
				<xsl:element name="NationalMarkRegistrationDate">
					<xsl:value-of select='concat(substring(NATRDAT,1,4),"-",substring(NATRDAT,5,2),"-",substring(NATRDAT,7,2))'/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="NATPDAT">
				<xsl:element name="NationalMarkPriorityDate">
					<xsl:value-of select='concat(substring(NATPDAT,1,4),"-",substring(NATPDAT,5,2),"-",substring(NATPDAT,7,2))'/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
</xsl:stylesheet>
