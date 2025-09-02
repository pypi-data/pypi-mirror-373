<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">

<!-- -->			
	<xsl:template name="makeRecordHeader">
		<xsl:param name="recordType"/>
		
		<xsl:variable name="regdate" select="@REGRDAT"/>
	
		<xsl:if test="$regdate!=''">
			<xsl:element name="RecordFilingDate">
				<xsl:value-of select='concat(substring(./@REGRDAT,1,4),"-",substring(./@REGRDAT,5,2),"-",substring(./@REGRDAT,7,2))'/>
			</xsl:element>
		</xsl:if>
		<xsl:if test="@NOTDATE">
			<xsl:element name="RecordNotificationDate">
				<xsl:value-of select='concat(substring(./@NOTDATE,1,4),"-",substring(./@NOTDATE,5,2),"-",substring(./@NOTDATE,7,2))'/>
			</xsl:element>
		</xsl:if>
		
		<xsl:if test="@REGEDAT">
			<xsl:element name="RecordEffectiveDate">
				<xsl:value-of select='concat(substring(./@REGEDAT,1,4),"-",substring(./@REGEDAT,5,2),"-",substring(./@REGEDAT,7,2))'/>
			</xsl:element>
		</xsl:if>
		
		<xsl:if test="$recordType!='skip'">
			<xsl:element name="{$recordType}">
				<xsl:choose>
					<xsl:when test="name()='APNE'">Appeal Expired</xsl:when>
					<xsl:when test="name()='APNL'">Appeal Lapsed</xsl:when>
					<xsl:when test="name()='APNW'">Appeal Withdrawn</xsl:when>
					<xsl:when test="name()='CBNO'">Other ceasing of effect</xsl:when>
					<xsl:when test="name()='CBNP'">Partial Ceasing Effect</xsl:when>
					<xsl:when test="name()='CBNT'">Total Ceasing Effect</xsl:when>
					<xsl:when test="name()='CBN1'">Judicial Action</xsl:when>
					<xsl:when test="name()='CEN'">Effect Continuation</xsl:when>
					<xsl:when test="name()='DIN'">Disclaimer</xsl:when>
					<xsl:when test="name()='DBN'">Division or Merger of Basic Registration</xsl:when>
					<xsl:when test="name()='EEN'">Renewal Under Rule 40.3</xsl:when>
					<xsl:when test="name()='ENN'">Registration</xsl:when>
					<xsl:when test="name()='EENN'">Non Renewal Under Rule 40.3</xsl:when>
					<xsl:when test="name()='EXN'">Subsequent Designation</xsl:when>
					<xsl:when test="name()='FDNP'">Rule 18ter(4) protected goods and services</xsl:when>
					<xsl:when test="name()='FDNT'">Rule 18ter(4) all goods and services refused</xsl:when>
					<xsl:when test="name()='FDNV'">Rule 18ter(4) all goods and services protected</xsl:when>
					<xsl:when test="name()='FINC'">Final Confirmation Refusal</xsl:when>
					<xsl:when test="name()='FINO'">Final Other Decision</xsl:when>
					<xsl:when test="name()='FINT'">Final Other Decision</xsl:when>
					<xsl:when test="name()='FINCD'">Final Other Decision</xsl:when>
					<xsl:when test="name()='FINVD'">Final Other Decision</xsl:when>
					<xsl:when test="name()='FINV'">Final Reversing Refusal</xsl:when>
					<xsl:when test="name()='FINVD'">Final Reversing Refusal</xsl:when>	
					<xsl:when test="name()='GPN'">Protection Granted</xsl:when>
					<xsl:when test="name()='GP18N'">Rule 18ter(1) GP without provisional refusal</xsl:when>		
					<xsl:when test="name()='GP18NA'">GP following Rule 18bis(1)(a) declaration (OP expired)</xsl:when>
					<xsl:when test="name()='HRN'">Holder Rights Restriction</xsl:when>
					<xsl:when test="name()='INNP'">Partial Invalidation</xsl:when>
					<xsl:when test="name()='INNT'">Total Invalidation</xsl:when>					
					<xsl:when test="name()='LIN'">Limitation</xsl:when>
					<xsl:when test="name()='LNN'">No Effect Limitation</xsl:when>
					<xsl:when test="name()='MAN'">Representative Appointed</xsl:when>
					<xsl:when test="name()='OBN'">Subsequent Designation Resulting From Conversion</xsl:when>
					<xsl:when test="name()='PCN'">Partial Cancellation</xsl:when>
					<xsl:when test="name()='P2N'">Second Part Fee Not Paid</xsl:when>
					<xsl:when test="name()='RAN'">Total Cancellation</xsl:when>
					<xsl:when test="name()='RCN'">Complementary Renewal</xsl:when>
					<xsl:when test="name()='REN'">Renewal</xsl:when>
					<xsl:when test="name()='REN2'">Non Renewal</xsl:when>
					<xsl:when test="name()='REN3'">Non Renewal Certain Parties</xsl:when>
					<xsl:when test="name()='RFNP'">Partial Refusal</xsl:when>
					<xsl:when test="name()='RFNT'">Total Refusal</xsl:when>
					<xsl:when test="name()='RHR'">Removal of holder Rights Restriction</xsl:when>
					<xsl:when test="name()='RNN'">Renunciation</xsl:when>
					<xsl:when test="name()='RTN'">Refusal Transfer of Ownership</xsl:when>
					<xsl:when test="name()='R18NP'">Rule 18ter(2)(ii) GP following a provisional refusal</xsl:when>
					<xsl:when test="name()='R18NPD'">Rule 18ter(2)(ii) GP following a provisional refusal (acceptation with reserve)</xsl:when>
					<xsl:when test="name()='R18NT'">Rule 18ter(3) Confirmation of total provisional refusal</xsl:when>
					<xsl:when test="name()='R18NV'">Rule 18ter(2)(i) GP following a provisional refusal</xsl:when>
					<xsl:when test="name()='R18NVD'">Rule 18ter(2)(i) GP  following a provisional refusal (acceptation with reserve)</xsl:when>
					<xsl:when test="name()='SEN'">Balance of Fees</xsl:when>
					<xsl:when test="name()='SNNA'">Seniority Added</xsl:when>
					<xsl:when test="name()='SNNR'">Seniority Removed</xsl:when>
					<xsl:when test="name()='UFINO'">Unpublished Other Final Decision</xsl:when>
					<xsl:when test="name()='URFNP'">Unpublished Partial Refusal</xsl:when>
					<!-- Short Notation -->
					<xsl:when test="name()='FUN'">Merger</xsl:when>
					<xsl:when test="name()='CPN'">Partial Transfer</xsl:when>
					<!-- Record Opposition Period -->
					<xsl:when test="name()='ISN'">Rule 18bis(1) Ex Officio examination completed but third parties opposition or observations possible</xsl:when>
					<xsl:when test="name()='OPN'">Opposition Period</xsl:when>
					<xsl:when test="name()='GPON'">Protection Granted Opposition Period</xsl:when>
					<!-- Licence -->
					<xsl:when test="name()='NLCN'">Licence</xsl:when>
					<xsl:when test="name()='LLCN'">Licensee Name Address Change</xsl:when>
					<xsl:when test="name()='RLCN'">License no Effect</xsl:when>
					<xsl:when test="name()='CLCN'">License Cancelled</xsl:when>
					<!-- Record Transfer -->
					<xsl:when test="name()='TRN'">Total Transfer</xsl:when>
					<xsl:when test="name()='MTN'">Holder</xsl:when>
				<xsl:otherwise/> 
			</xsl:choose>		
		</xsl:element>
		</xsl:if>
		<!-- -->		
		<xsl:if test="@DOCID">
			<xsl:element name="RecordReference">
				<xsl:value-of select="@DOCID"/>
			</xsl:element>
		</xsl:if>
		<!-- -->		
		<xsl:apply-templates select="@ORIGLAN|./PRF/@ORIGLAN|./UPRF/@ORIGLAN" mode="record"/>
		
		<xsl:if test="@GAZNO|@OGAZNO">
			<xsl:element name="RecordPublicationDetails">
				<xsl:if test="@OGAZNO">
					<xsl:element name="RecordPublication">
						<xsl:element name="PublicationIdentifier">
							<xsl:value-of select="@OGAZNO"/>
						</xsl:element>
						<xsl:if test="@OPUBDATE">
							<xsl:element name="PublicationDate">
								<xsl:value-of select='concat(substring(./@OPUBDATE,1,4),"-",substring(./@OPUBDATE,5,2),"-",substring(./@OPUBDATE,7,2))'/>
							</xsl:element>
						</xsl:if>
					</xsl:element>
				</xsl:if>
				<xsl:if test="@GAZNO">
					<xsl:element name="RecordPublication">
						<xsl:element name="PublicationIdentifier">
							<xsl:value-of select="@GAZNO"/>
						</xsl:element>
						<xsl:if test="@PUBDATE">
							<xsl:element name="PublicationDate">
								<xsl:value-of select='concat(substring(./@PUBDATE,1,4),"-",substring(./@PUBDATE,5,2),"-",substring(./@PUBDATE,7,2))'/>
							</xsl:element>		
						</xsl:if>						
					</xsl:element>
				</xsl:if>
			</xsl:element>
		</xsl:if>
	</xsl:template>
<!-- -->	
	<xsl:template match="@ORIGLAN" mode="record">
		<xsl:element name="RecordLanguageCode">
			<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="."/></xsl:with-param>
			</xsl:call-template>
		</xsl:element>
	</xsl:template>
</xsl:stylesheet>
