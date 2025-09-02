<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
<!--
Changes
05/10/2011 Roger Holberton   Correct output of CPN ( i.e. not FUN)
-->	
	<xsl:template name="makeShortNotationRecord">
			<xsl:element name="MarkRecord">
				<xsl:element name="RecordShortNotation">
					<xsl:call-template name="makeRecordHeader">
						<xsl:with-param name="recordType">RecordShortNotationKind</xsl:with-param>
					</xsl:call-template>
					<xsl:element name="RecordToRegistration">
						<xsl:element name="RegistrationIdentifier">	
							<xsl:if test="name()='FUN'">
								<xsl:value-of select="./NEWREGN"/>
							</xsl:if>
							<xsl:if test="name()!='FUN'">
								<xsl:value-of select="./INTREGG[2]/INTREGN"/>
							</xsl:if>
						</xsl:element>
					</xsl:element>
					<xsl:element name="RecordFromRegistrationDetails">
						<xsl:apply-templates select="./INTREGG[1]"/>
							<xsl:if test="name()='FUN'">
								<xsl:apply-templates select="./INTREGG[2]"/>
							</xsl:if>
					</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	<!-- For Fusions (for the time being...) -->
	<xsl:template match="INTREGG">
		<xsl:element name="RecordFromRegistration">
			<xsl:element name ="RegistrationIdentifier">
				<xsl:value-of select="./INTREGN"/>
			</xsl:element>
			<xsl:element name="MarkVerbalElementText">
				<xsl:value-of select="./MARKVE"/>
			</xsl:element>
			<xsl:if test="./AFFCP">
				<xsl:element name="DesignatedCountryDetails">
					<xsl:apply-templates select="./AFFCP"/>
				</xsl:element>
			</xsl:if>
			<xsl:if test="../LIMGR">
				<xsl:apply-templates select="../LIMGR"/>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="AFFCP" >
		<xsl:element name="DesignatedCountryCode">
			<xsl:value-of select="./@CPCD"/>
		</xsl:element>
	</xsl:template>
	

</xsl:stylesheet>
