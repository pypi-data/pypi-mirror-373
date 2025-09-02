<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fn="http://www.w3.org/2005/02/xpath-functions" xmlns="http://www.wipo.int/standards/XMLSchema/trademarks" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks http://www.wipo.int/standards/XMLSchema/trademarks/romarin/Romarin-V1-3.xsd">
	<!-- //www.wipo.int/standards/XMLSchema/trademarks/st66model-V1-1.xsd">-->
	<xsl:output encoding="utf-8"/>
	<!--
Changes
05/10/2011 Roger Holberton   Add MARTRAN
                             DesignatedUnderCode values as xsl:text
24/10/2011 Roger Holberton   Add MARTRAN as test to WordMark. Oops
01/12/2011 Roger Holberton   DESPG2 as ProtocolArticle9-6
02/04/2012 Roger Holberton   Check for contents before formatting dates
20/03/2014 Roger Holberton   Update version of Romarin schema to 1.2
18/04/2016 Roger Holberton   Check DCPCD not null
-->
	<xsl:param name="xsd"/>

	<xsl:variable name="xsdVersion">
	  <xsl:choose>
	    <xsl:when test="$xsd and $xsd = 'euipo'">euipo</xsl:when>
	    <xsl:otherwise>romarin</xsl:otherwise>
	  </xsl:choose>
	</xsl:variable>

	<xsl:variable name="namespace">
	  <xsl:choose>
	    <xsl:when test="$xsdVersion = 'romarin'">http://www.wipo.int/standards/XMLSchema/trademarks</xsl:when>
	    <xsl:when test="$xsdVersion = 'euipo'">http://www.oami.europa.eu/TM-Search</xsl:when>
	  </xsl:choose>
	</xsl:variable>

	<xsl:variable name="xmlnsXsi">http://www.w3.org/2001/XMLSchema-instance</xsl:variable>

	<!-- -->
	<xsl:template match="/">
		<!-- <xsl:element name="Transaction" namespace="{$namespace}"> -->
		<!--   <xsl:attribute name="xsi:schemaLocation">http://www.wipo.int/standards/XMLSchema/trademarks http://www.wipo.int/standards/XMLSchema/trademarks/romarin/Romarin-V1-3.xsd</xsl:attribute> -->
<!--
		  <xsl:if test="$xsdVersion = 'euipo'">
		    <xsl:attribute name="xmlns:xsi">http://www.w3.org/2001/XMLSchema-instance</xsl:attribute>
		  </xsl:if>
-->
			  <xsl:apply-templates select="node()"/>
          <!-- </xsl:element> -->
	</xsl:template>
	<!-- -->
	<xsl:template match="MARKGR">
		<xsl:variable name="nodeCount" select="count(child::*)"/>
		<xsl:element name="TradeMark">
			<xsl:apply-templates select="CURRENT" mode="mark-record"/>
			<xsl:if test="$nodeCount>1">
				<xsl:element name="MarkRecordDetails">
					<xsl:apply-templates select="node()"/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="CURRENT"/>

	<!-- -->
	<xsl:template match="FBN">
		<xsl:call-template name="makeNatIntReplacement"/>
	</xsl:template>
	<xsl:template match="NLCN|LLCN|CLCN|RLCN">
		<xsl:call-template name="makeLicenseRecord"/>
	</xsl:template>
	<xsl:template match="RAN|APNE|APNL|APNW|DIN|RTN|P2N|SEN|EEN|EENN|RNN|CEN|SNNA|SNNR|LNN|HRN|RHR|URFNP|UFINO|DBN">
		<xsl:call-template name="makeBasicRecord"/>
	</xsl:template>
	<xsl:template match="ENN|EXN|OBN|REN|RCN|REN2|REN3|RFNP|RFNT|FINC|FINO|FINV|FINT|FINVD|FINCD|INNP|INNT|PCN|LIN|CBNP|CBNT|CBNO|GPN|GP18N|GP18NA|R18NP|R18NPD|R18NT|R18NV|R18NVD|FDNP|FDNT|FDNV">
		<xsl:call-template name="makeBasicRecord"/>
	</xsl:template>
	<!-- -->
	<xsl:template match="ISN|GPON|OPN">
		<xsl:call-template name="makeOppositionPeriod"/>
	</xsl:template>
	<!-- -->
	<xsl:template match="CPN|FUN">
		<xsl:call-template name="makeShortNotationRecord"/>
	</xsl:template>
	<!-- -->
	<!-- ======================================================================================================== -->
	<!--  Here starts the processing of the "CURRENT" International Registration data  -->
	<!-- ======================================================================================================== -->
	<!-- -->
	<xsl:template match="CURRENT" mode="mark-record">
		<xsl:element name="RegistrationOfficeCode">
			<xsl:text>WO</xsl:text>
		</xsl:element>
		<!-- -->
		<xsl:element name="ReceivingOfficeCode">
			<xsl:value-of select="../@OOCD"/>
		</xsl:element>
		<!-- -->
		<xsl:if test="../@INTREGN">
			<xsl:element name="ApplicationNumber">
				<xsl:value-of select="../@INTREGN"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="../@INTREGD and string-length(../@INTREGD) &gt; 0">
			<xsl:element name="ApplicationDate">
				<xsl:value-of select='concat(substring(../@INTREGD,1,4),"-",substring(../@INTREGD,5,2),"-",substring(../@INTREGD,7,2))'/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="../@ORIGLAN">
			<xsl:element name="ApplicationLanguageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="../@ORIGLAN"/></xsl:with-param>
				</xsl:call-template>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="../@SECLAN">
			<xsl:element name="SecondLanguageCode">
				<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="../@SECLAN"/></xsl:with-param>
				</xsl:call-template>
			</xsl:element>
		</xsl:if>
		<xsl:if test="../@EXPDATE and string-length(../@EXPDATE) &gt; 0">
			<xsl:element name="ExpiryDate">
				<xsl:value-of select='concat(substring(../@EXPDATE,1,4),"-",substring(../@EXPDATE,5,2),"-",substring(../@EXPDATE,7,2))'/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="(./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD)">
			<xsl:element name="DesignatedCountryDetails">
				<xsl:apply-templates select="./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="./PREREGG">
			<xsl:element name="PreviousRegistrationDetails">
				<xsl:apply-templates select="./PREREGG"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="./BASGR">
			<xsl:element name="BasicRegistrationApplicationDetails">
				<xsl:apply-templates select="./BASGR"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:element name="KindMark">
			<xsl:if test="./TYPMARI">
				<xsl:text>Collective</xsl:text>
			</xsl:if>
			<xsl:if test="not(./TYPMARI)">
				<xsl:text>Individual</xsl:text>
			</xsl:if>
		</xsl:element>
		<!-- -->
		<xsl:element name="MarkFeature">
			<xsl:choose>
				<xsl:when test="./STDMIND">
					<xsl:text>Word</xsl:text>
				</xsl:when>
				<xsl:when test="./COLMARI">
					<xsl:text>Colour</xsl:text>
				</xsl:when>
				<xsl:when test="./THRDMAR">
					<xsl:text>3-D</xsl:text>
				</xsl:when>
				<xsl:when test="./SOUMARI">
					<xsl:text>Sound</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:text>Figurative</xsl:text>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
		<!-- -->
		<xsl:apply-templates select="./MARDESGR|./VOLDESGR"/>    <!-- wipo.romarin.markdescription.xsl -->
		<!-- <xsl:apply-templates select="./MARTRAN"/>     wipo.romarin.markdescription.xsl -->
		<!-- -->
		<xsl:apply-templates select="./DISCLAIMGR"/> <!-- wipo.romarin.markdescription.xsl -->
		<!-- -->
		<xsl:if test="./IMAGE/@TEXT or ./MARTRAN">
				<xsl:call-template name="makeWordMarkSpecification"/> <!-- wipo.romarin.markdescription.xsl -->
		</xsl:if>
		<!-- -->
		<xsl:variable name="filetype" select="./IMAGE/@TYPE"/>
		<xsl:if test="$filetype!='NIL'">
			<xsl:apply-templates select="./IMAGE"/> <!-- wipo.romarin.markdescription.xsl -->
		</xsl:if>
		<!-- -->
		<xsl:apply-templates select="./BASICGS"/>
		<!-- -->
		<xsl:if test="./PRIGR">
			<xsl:element name="PriorityDetails">
				<xsl:apply-templates select="./PRIGR"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:call-template name="makeSeniority"/>
		<!-- -->
		<xsl:element name="ApplicantDetails">
			<xsl:apply-templates select="./HOLGR" mode="details"/>
		</xsl:element>
		<!-- -->
		<xsl:if test="./REPGR">
			<xsl:element name="RepresentativeDetails">
				<xsl:apply-templates select="./REPGR" mode="details"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:choose>
			<xsl:when test="./CORRGR">
				<xsl:apply-templates select="./CORRGR"/>
			</xsl:when>
			<xsl:otherwise>
				<xsl:if test="./HOLGR/CORRIND">
					<xsl:apply-templates select="./HOLGR/CORRIND" />
				</xsl:if>
			</xsl:otherwise>
		</xsl:choose>
		<!-- -->
		<xsl:if test="PHOLGR">
			<xsl:element name="PreviousHolderDetails">
				<xsl:apply-templates select="./PHOLGR" mode="details"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
		<xsl:if test="./MARDUR">
			<xsl:element name="InternationalRegistrationDuration">
				<xsl:value-of select="./MARDUR"/>
			</xsl:element>
		</xsl:if>
		<xsl:if  test ="./NATDECGR/NATDECEN|./NATDECGR/NATDECFR|./NATDECGR/NATDECES">
			<xsl:element name="InternationalRegistrationNationalDeclarationDetails">
				 <xsl:apply-templates select="./NATDECGR/NATDECEN|./NATDECGR/NATDECFR|./NATDECGR/NATDECES"/>
			 </xsl:element>
		</xsl:if>
		<xsl:apply-templates select="./INTENTG"/>
	</xsl:template>
	<!--  Here ends the <TradeMark> ===================================================================================== -->
		<!-- -->
	<xsl:template match="DESAG/DCPCD">
		<xsl:element name="DesignatedCountry">
			<xsl:element name="DesignatedCountryCode">
				<xsl:value-of select="text()"/>
			</xsl:element>
			<xsl:element name="DesignatedUnderCode">
				<xsl:text>Agreement</xsl:text>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<xsl:template match="DESPG/DCPCD">
		<xsl:element name="DesignatedCountry">
			<xsl:element name="DesignatedCountryCode">
				<xsl:value-of select="text()"/>
			</xsl:element>
			<xsl:element name="DesignatedUnderCode">
				<xsl:text>Protocol</xsl:text>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<xsl:template match="DESPG2/DCPCD">
		<xsl:element name="DesignatedCountry">
			<xsl:element name="DesignatedCountryCode">
				<xsl:value-of select="text()"/>
			</xsl:element>
			<xsl:element name="DesignatedUnderCode">
				<xsl:text>ProtocolArticle9-6</xsl:text>
			</xsl:element>
		</xsl:element>
	</xsl:template>

	<!-- -->
	<xsl:template match="DCPCD" mode="limitation">
		<xsl:if test="text()!=''">
			<xsl:element name="LimitationCountryCode">
				<xsl:value-of select="."/>
			</xsl:element>
		</xsl:if>
	</xsl:template>
	<!-- -->
	<xsl:template match="DCPCD" mode="nonrenewal">
		<xsl:element name="DesignatedCountry">
			<xsl:element name="DesignatedCountryCode">
				<xsl:value-of select="."/>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<!-- ======================================================================================================== -->
	<xsl:template match="BASGR">
			<xsl:element name="BasicRegistrationApplication">
				<xsl:if test="BASAPPGR">
					<xsl:element name="BasicApplicationDetails">
						<xsl:apply-templates select="BASAPPGR"/>
					</xsl:element>
				</xsl:if>
				<xsl:if test="BASREGGR">
					<xsl:element name="BasicRegistrationDetails">
						<xsl:apply-templates select="BASREGGR"/>
					</xsl:element>
				</xsl:if>
			</xsl:element>
	</xsl:template>
	<xsl:template match="BASAPPGR">
		<xsl:element name="BasicApplication">
			<xsl:element name="BasicApplicationNumber">
			<xsl:value-of select="./BASAPPN"/>
		</xsl:element>
		<xsl:if test="string-length(BASAPPD) &gt; 0">
			<xsl:element name="BasicApplicationDate">
				<xsl:value-of select='concat(substring(./BASAPPD,1,4),"-",substring(./BASAPPD,5,2),"-",substring(./BASAPPD,7,2))'/>
			</xsl:element>
		</xsl:if>
	</xsl:element>
	</xsl:template>
	<xsl:template match="BASREGGR">
		<xsl:element name="BasicRegistration">
			<xsl:element name="BasicRegistrationNumber">
				<xsl:value-of select="./BASREGN"/>
			</xsl:element>
		<xsl:if test="string-length(BASREGD) &gt; 0">
			<xsl:element name="BasicRegistrationDate">
				<xsl:value-of select='concat(substring(./BASREGD,1,4),"-",substring(./BASREGD,5,2),"-",substring(./BASREGD,7,2))'/>
			</xsl:element>
		</xsl:if>
		</xsl:element>
	</xsl:template>
	<!-- -->

	<xsl:template match="INTENTG">
		<xsl:element name ="MarkUseIntentDetails">
			<xsl:for-each select="CPCD">
				<xsl:element name="MarkUseIntentCountryCode">
					<xsl:value-of select="."/>
				</xsl:element>
			</xsl:for-each>
		</xsl:element>

	</xsl:template>
	<!-- -->
	<!-- ======================================================================================================== -->
		<xsl:template match="NATDECEN|NATDECFR|NATDECES">
			<xsl:element name="NationalDeclaration">
				<xsl:attribute name="languageCode">
					<xsl:call-template name="makeLanguage">
						<xsl:with-param name="lang"><xsl:value-of select="name()"/></xsl:with-param>
					</xsl:call-template>
				</xsl:attribute>
				<xsl:value-of select="."/>
			</xsl:element>
		</xsl:template>
	<!-- ======================================================================================================== -->
	<xsl:template match="PREREGG">
		<xsl:element name="PreviousRegistration">
			<xsl:element name="PreviousRegistrationNumber">
				<xsl:value-of select="PREREGN"/>
			</xsl:element>
			<xsl:if test="PREREGD">
				<xsl:element name="PreviousRegistrationDate">
					<xsl:value-of select='concat(substring(./PREREGD,1,4),"-",substring(./PREREGD,5,2),"-",substring(./PREREGD,7,2))'/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->

	<xsl:template match="PENN">
	  <xsl:apply-templates select="IBRCPTDT"/>
	  <xsl:apply-templates select="OORCPTDT"/>
	  <xsl:apply-templates select="STATUS"/>
		<!-- -->
		<xsl:if test="(./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD)">
			<xsl:element name="DesignatedCountryDetails">
				<xsl:apply-templates select="./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
	</xsl:template>

	<xsl:template match="PEXN">
	  <xsl:apply-templates select="IBRCPTDT"/>
	  <xsl:apply-templates select="OORCPTDT"/>
	  <xsl:apply-templates select="STATUS"/>
		<!-- -->
		<xsl:if test="(./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD)">
			<xsl:element name="DesignatedCountryDetails">
				<xsl:apply-templates select="./DESAG/DCPCD|./DESPG/DCPCD|./DESPG2/DCPCD"/>
			</xsl:element>
		</xsl:if>
		<!-- -->
	</xsl:template>

	<xsl:template match="STATUS">
	  <xsl:element name="WO_PendingStatus"><xsl:value-of select="."/></xsl:element>
    </xsl:template>

	<xsl:template match="IBRCPTDT">
        <xsl:element name="WO_IBReceiptDate">
            <xsl:value-of select='concat(substring(.,1,4),"-",substring(.,5,2),"-",substring(.,7,2))'/>
        </xsl:element>
	</xsl:template>

	<xsl:template match="OORCPTDT">
	    <xsl:element name="WO_OOReceiptDate">
            <xsl:value-of select='concat(substring(.,1,4),"-",substring(.,5,2),"-",substring(.,7,2))'/>
        </xsl:element>
	</xsl:template>

	<xsl:include href="wipo.romarin.basicrecord.xsl"/>
	<xsl:include href="wipo.romarin.shortnotation.xsl"/>
	<xsl:include href="wipo.romarin.oppositionper.xsl"/>
	<xsl:include href="wipo.romarin.licenserecord.xsl"/>
	<xsl:include href="wipo.romarin.natintreplacement.xsl"/>
	<!-- -->
	<xsl:include href="wipo.romarin.markdescription.xsl"/>
	<xsl:include href="wipo.romarin.gsbasicandlim.xsl"/>
	<xsl:include href="wipo.romarin.priority.xsl"/>
	<xsl:include href="wipo.romarin.seniority.xsl"/>
	<xsl:include href="wipo.romarin.holderandrep.xsl"/>
	<xsl:include href="wipo.romarin.recordheader.xsl"/>
	<xsl:include href="wipo.romarin.utilities.xsl"/>
	<!-- -->
</xsl:stylesheet>
