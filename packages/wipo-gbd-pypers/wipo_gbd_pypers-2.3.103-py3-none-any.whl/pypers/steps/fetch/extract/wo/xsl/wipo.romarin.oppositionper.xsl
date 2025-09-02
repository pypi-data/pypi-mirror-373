
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
	<xsl:template name="makeOppositionPeriod">
			<xsl:element name="MarkRecord">
				<xsl:element name="RecordOppositionPeriod">
					<xsl:call-template name="makeRecordHeader">
						<xsl:with-param name="recordType">RecordOppositionPeriodKind</xsl:with-param>
					</xsl:call-template>
					<xsl:if test="@INTOFF">
						<xsl:element name="RecordInterestedOfficeCode">
							<xsl:value-of select="@INTOFF"/>
						</xsl:element>
					</xsl:if>
					<xsl:if test="@OPPERE">
						<xsl:element name="RecordOppositionPeriodEndDate">	
							<xsl:value-of select='concat(substring(./@OPPERE,1,4),"-",substring(./@OPPERE,5,2),"-",substring(./@OPPERE,7,2))'/>
						</xsl:element>
					</xsl:if>
					<xsl:if test="OPPERS">
						<xsl:element name="RecordOppositionPeriodStartDate">	
							<xsl:value-of select='concat(substring(./OPPERS,1,4),"-",substring(./OPPERS,5,2),"-",substring(./OPPERS,7,2))'/>
						</xsl:element>
					</xsl:if>
					<xsl:if test="OPPERE">
						<xsl:element name="RecordOppositionPeriodEndDate">	
							<xsl:value-of select='concat(substring(./OPPERE,1,4),"-",substring(./OPPERE,5,2),"-",substring(./OPPERE,7,2))'/>
						</xsl:element>
					</xsl:if>
			</xsl:element>
		</xsl:element>
	</xsl:template>

</xsl:stylesheet>
