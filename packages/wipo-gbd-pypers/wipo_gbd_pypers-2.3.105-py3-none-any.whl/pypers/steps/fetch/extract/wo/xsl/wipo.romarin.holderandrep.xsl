
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" 
xmlns="http://www.wipo.int/standards/XMLSchema/trademarks"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xsi:schemaLocation="http://www.wipo.int/standards/XMLSchema/trademarks D:\Eclipse\RomarinWork\romarin\Romarin-V1-1.xsd">
	

	<!-- ======================================================================================================== -->
	<!-- Changes
	 09/11/2011 Roger Holberton  Remove LEGNATU/PLAINCO for Licensee - not in Romarin XSD
	 22/01/2013 Roger Holberton  Filter out some invalid Nationality codes
	                             Only put entitlementAddress when country code
	 18/03/2014 Roger Holberton  Add CorrespondenceAddressIdentifier
	 07/07/2014 Roger Holberton  Add Check ENTADDR/COUNTRY has content
	 15/08/2014 Roger Holberton  Do above for ENTDOM too
	 19/08/2015 Roger Holberton  Change COUNTRY=BX to NL
	 09/11/2015 Roger Holberton  Change NATLTY=BX to NL
	 06/02/2018 Roger Holberton  Don't process CORRIND
	 -->
	<!-- -->
	<xsl:template match="CORRGR">
		<xsl:element name="CorrespondenceAddress">
			<xsl:element name="CorrespondenceAddressIdentifier">
				<xsl:value-of select="@CLID"/>
			</xsl:element>
			<xsl:element name="CorrespondenceAddressParty">
					<xsl:text>Applicant</xsl:text>
			</xsl:element>
			<xsl:element name="CorrespondenceAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
					<xsl:apply-templates select="ADDRESS"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="CORRIND"/>
	<xsl:template match="CORRINDx">
		<xsl:element name="CorrespondenceAddress">
			<xsl:element name="CorrespondenceAddressIdentifier">
				<xsl:value-of select="../@CLID"/>
			</xsl:element>
			<xsl:element name="CorrespondenceAddressParty">
				<xsl:text>Applicant</xsl:text>
			</xsl:element>
			<xsl:element name="CorrespondenceAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="../NAME"/>
					<xsl:apply-templates select="../ADDRESS"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- ApplicantDetails -->
	<xsl:template match="HOLGR">
		<xsl:element name="Applicant">
			<xsl:element name="ApplicantIdentifier">
				<xsl:value-of select="/MARKGR/@INTREGN"/>
			</xsl:element>
			<xsl:element name="ApplicantAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
					
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="HOLGR|PHOLGR" mode="details">
		<xsl:element name="Applicant">
			<xsl:element name="ApplicantIdentifier">
				<xsl:value-of select="@CLID"/>
			</xsl:element>
			<xsl:apply-templates select="NATLTY"/>
			<xsl:apply-templates select="LEGNATU/LEGNATT"/>   
			<xsl:apply-templates select="LEGNATU/PLAINCO"/>   
			<xsl:element name="ApplicantAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
					<xsl:apply-templates select="ADDRESS"/>
				</xsl:element>
			</xsl:element>
			<xsl:if test="ENTNATL|ENTEST|ENTDOM">
				<xsl:element name="ApplicantEntitlement">
					<xsl:apply-templates select="ENTNATL"/> 
					<xsl:apply-templates select="ENTEST"/>
					<xsl:apply-templates select="ENTDOM"/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="NAME">
		<xsl:element name="Name">
			<xsl:element name="FreeFormatName">
				<xsl:element name="FreeFormatNameDetails">
					<xsl:apply-templates select="@*|node()"/>
				</xsl:element>
			</xsl:element>
			<xsl:if test="../NAMETR">
				<xsl:element name="NameTransliteration">
					<xsl:value-of select="../NAMETR"/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<xsl:template match="NAMEL">
		<xsl:element name="FreeFormatNameLine">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="ENTNATL">
		<xsl:element name="EntitlementNationalityCode">
			<xsl:choose>
				<xsl:when test="text()='DD'">
					<xsl:text>DE</xsl:text>
				</xsl:when>
				<xsl:when test="text()='DT'">
					<xsl:text>DE</xsl:text>
				</xsl:when>
				<xsl:when test="text()='SU'">
					<xsl:text>RU</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="."/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	<xsl:template match="ENTEST">
		<xsl:element name="EntitlementEstablishment">
			<xsl:element name="EntitlementEstablishmentCode">
				<xsl:value-of select="."/>
			</xsl:element>
	<!--		<xsl:if test="name(following-sibling::*[1])='ENTADDR'"> -->
  		<xsl:if test="following-sibling::ENTADDR[1]/COUNTRY!=''">
				<xsl:element name="EntitlementEstablishmentAddressBook">
					<xsl:call-template name="makeEntitlementAddress"/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<xsl:template match="ENTDOM">
		<xsl:element name="EntitlementDomiciled">
			<xsl:element name="EntitlementDomiciledCode">
				<xsl:value-of select="."/>
			</xsl:element>
 <!--			<xsl:if test="following-sibling::ENTADDR[1]/COUNTRY"> 	 -->
   		<xsl:if test="following-sibling::ENTADDR[1]/COUNTRY!=''">
  							<xsl:element name="EntitlementDomiciledAddressBook">
					<xsl:call-template name="makeEntitlementAddress"/>
				</xsl:element>
			</xsl:if>
		</xsl:element>
	</xsl:template>
	<xsl:template name="makeEntitlementAddress">
		<xsl:element name="FormattedNameAddress">
			<xsl:element name="Address">
				<xsl:apply-templates select="following-sibling::ENTADDR[1]/COUNTRY"/>
				<xsl:element name="FreeFormatAddress">
					<xsl:apply-templates select="following-sibling::ENTADDR[1]/ADDRL"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
<!-- -->
	<!--  -->
	<xsl:template match="HOLGR/@NOTLANG">
		<xsl:element name="AddressLanguageCode">
			<xsl:call-template name="makeLanguage">
					<xsl:with-param name="lang"><xsl:value-of select="HOLGR/@NOTLANG"/></xsl:with-param>
			</xsl:call-template>
		</xsl:element>
	</xsl:template>
	<xsl:template match="HOLGR/@CLID">
		<xsl:element name="ApplicantIdentifier">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>

	<xsl:template match="NATLTY">
		<xsl:element name="ApplicantNationalityCode">
			<xsl:choose>
				<xsl:when test="text()='DD'">
					<xsl:text>DE</xsl:text>
				</xsl:when>
				<xsl:when test="text()='DT'">
					<xsl:text>DE</xsl:text>
				</xsl:when>
				<xsl:when test="text()='SU'">
					<xsl:text>RU</xsl:text>
				</xsl:when>
				<xsl:when test="text()='BX'"> <!-- todo: look at address country -->
					<xsl:text>NL</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="."/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>

	<xsl:template match="LEGNATT">
		<xsl:element name="ApplicantLegalEntity">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="LEGNATT" mode="licensee" >
		<xsl:element name="LicenseeLegalEntity">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="PLAINCO">
		<xsl:element name="ApplicantIncorporationState">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>
	
	<xsl:template match="PLAINCO" mode="licensee">
		<xsl:element name="LicenseeIncorporationState">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>
	
	<!-- -->
	<!-- ======================================================================================================== -->
	<!-- -->
	<!-- RepresentativeDetails -->
	<xsl:template match="REPGR">
		<xsl:element name="Representative">
			<xsl:element name="RepresentativeIdentifier">
				<xsl:value-of select="/MARKGR/@INTREGN"/>
			</xsl:element>
			<xsl:element name="RepresentativeAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- RepresentativeDetails -->
	<xsl:template match="REPGR" mode="details">
		<xsl:element name="Representative">
			<xsl:apply-templates select="@CLID"/>
			<xsl:element name="RepresentativeAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
					<xsl:apply-templates select="ADDRESS"/>
				</xsl:element>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="REPGR/@CLID">
		<xsl:element name="RepresentativeIdentifier">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- -->
	<!-- -->
	<!-- ======================================================================================================== -->
	<!-- -->
	<!-- Licensee Details -->
	<xsl:template match="LCSEEGR|PLCSEEGR">
		<xsl:element name="Licensee">
			<xsl:apply-templates select="@CLID"/>
			<xsl:element name="LicenseeAddressBook">
				<xsl:element name="FormattedNameAddress">
					<xsl:apply-templates select="NAME"/>
					<xsl:apply-templates select="ADDRESS"/>
				</xsl:element>
			</xsl:element>
			<xsl:apply-templates select="LEGNATU/LEGNATT" mode="licensee" />   
	<!--		<xsl:apply-templates select="LEGNATU/PLAINCO" mode="licensee" />   -->
		</xsl:element>
	</xsl:template>
	<!-- -->
	<xsl:template match="LCSEEGR/@CLID">
		<xsl:element name="LicenseeIdentifier">
			<xsl:value-of select="."/>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	
	<xsl:template match="ADDRESS">
		<xsl:element name="Address">
			<xsl:apply-templates select="COUNTRY"/>
			<xsl:element name="FreeFormatAddress">
				<xsl:apply-templates select="ADDRL"/>
			</xsl:element>
		</xsl:element>
	</xsl:template>
	<xsl:template match="ADDRL">
		<xsl:element name="FreeFormatAddressLine">
			<xsl:apply-templates select="node()"/>
		</xsl:element>
	</xsl:template>
	<xsl:template match="COUNTRY">
		<xsl:element name="AddressCountryCode">
			<xsl:choose>
				<xsl:when test=".='BX'">
					<xsl:text>NL</xsl:text>
				</xsl:when>
				<xsl:otherwise>
					<xsl:apply-templates select="node()"/>
				</xsl:otherwise>
			</xsl:choose>
		</xsl:element>
	</xsl:template>
	<!-- ======================================================================================================== -->
	
	

</xsl:stylesheet>
