<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
	
	<xsl:template name="makeSeniority">
		<xsl:if test="./SENGRP">
			<xsl:element name="SeniorityDetails">
				<xsl:apply-templates select="./SENGRP"/>
			</xsl:element>
		</xsl:if>
	</xsl:template>
	<xsl:template match="SENGRP">
		<xsl:element name="Seniority">
			<xsl:element name="SeniorityCountryCode">
				<xsl:value-of select="./COUNTRY"/>
			</xsl:element>
			<xsl:if test="./PRIDATE">
				<xsl:element name="SeniorityPriorityDate">
					<xsl:value-of select='concat(substring(./PRIDATE,1,4),"-",substring(./PRIDATE,5,2),"-",substring(./PRIDATE,7,2))'/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="./FILINGNUMBER">
				<xsl:element name="SeniorityApplicationNumber">
					<xsl:value-of select="./FILINGNUMBER"/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="./FILINGDATE">
				<xsl:element name="SeniorityApplicationDate">
					<xsl:value-of select='concat(substring(./FILINGDATE,1,4),"-",substring(./FILINGDATE,5,2),"-",substring(./FILINGDATE,7,2))'/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="./REGNUMBER">
				<xsl:element name="SeniorityRegistrationNumber">
					<xsl:value-of select="./REGNUMBER"/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="./REGDATE">
				<xsl:element name="SeniorityRegistrationDate">
					<xsl:value-of select='concat(substring(./REGDATE,1,4),"-",substring(./REGDATE,5,2),"-",substring(./REGDATE,7,2))'/>
				</xsl:element>
			</xsl:if>
			<xsl:element name="InternationalTradeMarkCode">
				<xsl:value-of select="@nature"/>
			</xsl:element>
			<xsl:element name="SeniorityPartialIndicator">
				<xsl:choose>
					<xsl:when test="./TYPE">
						<xsl:if test="./TYPE='Partial'">true</xsl:if>
						<xsl:if test="./TYPE='Whole'">false</xsl:if>
					</xsl:when>
					<xsl:otherwise>false</xsl:otherwise>
				</xsl:choose>
			</xsl:element>
		</xsl:element>
	</xsl:template>
</xsl:stylesheet>
