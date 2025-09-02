
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fn="http://www.w3.org/2005/02/xpath-functions" xmlns="http://www.wipo.int/standards/XMLSchema/trademarks" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks http://www.wipo.int/standards/XMLSchema/trademarks/romarin/Romarin-V1-0.xsd">
	
	<xsl:template name="makeTransferRecord">
			<xsl:element name="MarkRecord">
				<xsl:element name="RecordTransfer">
					<xsl:call-template name="makeRecordHeader">
						<xsl:with-param name="recordType">RecordTransferKind</xsl:with-param>
					</xsl:call-template>
					<xsl:element name="RepresentativeDetails">
						<xsl:apply-templates select="REPGR" mode="details"/>
					</xsl:element>
					<xsl:apply-templates select="CORRGR"/>
					<xsl:element name="HolderDetails">
						<xsl:apply-templates select="PHOLGR" mode="details"/>
						<xsl:apply-templates select="HOLGR" mode="details"/>
					</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	
	
	

</xsl:stylesheet>
