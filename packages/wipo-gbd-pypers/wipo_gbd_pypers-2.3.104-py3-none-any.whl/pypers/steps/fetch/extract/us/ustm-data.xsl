<?xml version='1.0' encoding='UTF-8'?>
<xsl:stylesheet
 xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
 version="1.0">
  <xsl:output method="xml"
              encoding="UTF-8"
              indent="yes"/>
<xsl:variable name="CC">US</xsl:variable>
<xsl:variable name="language" select="'en'"/>
<xsl:variable name="tagnames-fileName" select="'ustm-tagnames.xml'"/>
<xsl:key name="tagName-lookup" match="tag" use="code"/>
<xsl:variable name="tagNames-top" select="document($tagnames-fileName)/tags"/>

<xsl:template name="getTagDescription">

<xsl:param name="tagName"/>
<xsl:param name="textType"/>
<xsl:param name="lowerCase"/>

<xsl:variable name="textField">
	<xsl:choose>
		<xsl:when test="$textType"><xsl:value-of select="$textType"/></xsl:when>
		<xsl:otherwise>short</xsl:otherwise>
	</xsl:choose>
</xsl:variable>
<xsl:variable name="testTagText">
	<xsl:choose>
		<xsl:when test="$textField = 'short'">
			<xsl:for-each select="$tagNames-top">
				<xsl:value-of select="key(&quot;tagName-lookup&quot;, $tagName)/short[not(@la) or (@la = $language)]"/>
			</xsl:for-each>
		</xsl:when>
		<xsl:otherwise>
			<xsl:for-each select="$tagNames-top">
				<xsl:value-of select="key(&quot;tagName-lookup&quot;, $tagName)/*[name() = $textField][not(@la) or (@la = $language)]"/>
			</xsl:for-each>
		</xsl:otherwise>
	</xsl:choose>
</xsl:variable>
<xsl:variable name="tagText">
	<xsl:choose>
<xsl:when test="$textField = 'heading' and not($testTagText)">
	<xsl:for-each select="$tagNames-top">
		<xsl:value-of select="key(&quot;tagName-lookup&quot;, $tagName)/short[@la = $language]"/>
	</xsl:for-each>
</xsl:when>
<xsl:otherwise>
	<xsl:value-of select="$testTagText"/>
</xsl:otherwise>
	</xsl:choose>
	</xsl:variable>
<xsl:choose>
	<xsl:when test="$tagText and $lowerCase"><xsl:value-of select="translate($tagText, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')"/></xsl:when>
	<xsl:when test="$tagText"><xsl:value-of select="$tagText"/></xsl:when>
	<xsl:otherwise><xsl:value-of select="$tagName"/></xsl:otherwise>
</xsl:choose>
</xsl:template>

<xsl:template match="/">
  <xsl:element name="RECORD">
    <xsl:element name="SOURCE">USTM</xsl:element>
    <xsl:apply-templates select="file"/>
  </xsl:element>
</xsl:template>

<xsl:template match="file">
    <xsl:variable name="zstatus">
        <xsl:call-template name="getTagDescription"><xsl:with-param name="textType" select="'statusCode'"/><xsl:with-param name="tagName">status<xsl:value-of select="head/statusCode"/></xsl:with-param></xsl:call-template>
    </xsl:variable>
    <xsl:element name="STATUS"><xsl:value-of select="$zstatus"/></xsl:element>
    <xsl:element name="CS">
       <xsl:call-template name="getTagDescription"><xsl:with-param name="textType">status</xsl:with-param><xsl:with-param name="tagName">status<xsl:value-of select="head/statusCode"/></xsl:with-param></xsl:call-template> 
    </xsl:element>

    <!-- <xsl:element name="CS"> -->
    <!--     <xsl:value-of select="head/statusCode"/>, <xsl:call-template name="getTagDescription"><xsl:with-param name="textType">status</xsl:with-param><xsl:with-param name="tagName">status<xsl:value-of select="head/statusCode"/></xsl:with-param></xsl:call-template>, <xsl:call-template name="getTagDescription"><xsl:with-param name="tagName">status<xsl:value-of select="head/statusCode"/></xsl:with-param></xsl:call-template> -->
  <!-- </xsl:element> -->


    <xsl:call-template name="dataTypes">
        <xsl:with-param name="status" select="$zstatus"/>
    </xsl:call-template>

    <xsl:apply-templates select="@action"><xsl:with-param name="tag" select="'DTY'"/></xsl:apply-templates>
    <xsl:element name="ID">USTM.<xsl:value-of select="serNum"/></xsl:element>
    <xsl:apply-templates select="head/mark"><xsl:with-param name="tag" select="'BRAND'"/></xsl:apply-templates>
    <xsl:apply-templates select="stmts/stmt[substring(typeCode, 1, 2) = 'PM']/text"><xsl:with-param name="tag" select="'PSEUDO'"/></xsl:apply-templates>
    <xsl:apply-templates select="regNum"/>
    <xsl:apply-templates select="stmts/stmt[substring(typeCode, 1, 2) = 'GS']/text"><xsl:with-param name="tag" select="'GS_EN'"/></xsl:apply-templates>
    <xsl:apply-templates select="serNum"><xsl:with-param name="tag" select="'AN'"/></xsl:apply-templates>
    <xsl:apply-templates select="head/fileDate"><xsl:with-param name="tag" select="'AD'"/></xsl:apply-templates>
    <xsl:apply-templates select="head/regDate"><xsl:with-param name="tag" select="'RD'"/></xsl:apply-templates>
    <xsl:choose>
        <xsl:when test="head/cancelDate">
            <xsl:apply-templates select="head/cancelDate"><xsl:with-param name="tag" select="'ED'"/></xsl:apply-templates>
        </xsl:when>
        <xsl:when test="head/abDate">
            <xsl:apply-templates select="head/abDate"><xsl:with-param name="tag" select="'ED'"/></xsl:apply-templates>
        </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="desSearches/desSearch"/>
    <xsl:apply-templates select="classes/class/intCode"/>
    <xsl:apply-templates select="classes/class/usCode"><xsl:with-param name="tag" select="NGC"/></xsl:apply-templates>
    <xsl:element name="OO">US</xsl:element>
    <xsl:apply-templates select="owners"/>
    <xsl:apply-templates select="head/domRep|head/attName"><xsl:with-param name="tag" select="'RP_EN'"/></xsl:apply-templates>

    <xsl:apply-templates select="intReg"/>

    <xsl:element name="DS">US</xsl:element>
</xsl:template>

<xsl:template match="intReg">
    <xsl:element name="irn_s"><xsl:value-of select="intRegNum"/></xsl:element>
</xsl:template>

<xsl:template name="dataTypes">
  <xsl:param name="status"/>
  <xsl:if test="head/mark and string-length(normalize-space(head/mark)) &gt; 0">
    <xsl:element name="ITY">Word</xsl:element>
  </xsl:if>
  <xsl:variable name="drawCode"><xsl:value-of select="substring(/file/head/drawCode, 1, 1)"/></xsl:variable>

  <xsl:choose>
    <xsl:when test="$drawCode = '2'"><xsl:element name="MTY">Figurative</xsl:element></xsl:when>
    <xsl:when test="$drawCode = '3'"><xsl:element name="MTY">Combined</xsl:element></xsl:when>
    <xsl:when test="$drawCode = '4'"><xsl:element name="MTY">Word</xsl:element></xsl:when>
    <xsl:when test="$drawCode = '5'"><xsl:element name="MTY">Stylized</xsl:element></xsl:when>
    <xsl:when test="$drawCode = '6'"><xsl:element name="MTY">Other</xsl:element></xsl:when>
    <xsl:otherwise>
      <xsl:choose>
        <xsl:when test="$drawCode = ' ' and $status = 'PEND'">
            <xsl:element name="ITY">Device</xsl:element>
            <xsl:element name="MTY">Combined</xsl:element>
        </xsl:when>
        <xsl:otherwise>
            <xsl:element name="ITY">Word</xsl:element>
            <xsl:element name="MTY">Word</xsl:element>
        </xsl:otherwise>
      </xsl:choose>
    </xsl:otherwise>
  </xsl:choose>

  <xsl:if test="string-length($drawCode) &gt; 0 and ($drawCode = '2' or $drawCode = '3') and string-length(serNum) &gt; 0">
    <xsl:element name="ITY">Device</xsl:element>
  </xsl:if>

  <xsl:if test="string-length($drawCode) &gt; 0 and ($drawCode = '5') and string-length(serNum) &gt; 0">
    <xsl:element name="ITY">Stylized</xsl:element>
  </xsl:if>

  <xsl:if test="string-length($drawCode) &gt; 0 and ($drawCode = '6') and string-length(serNum) &gt; 0">
    <xsl:element name="ITY">Other</xsl:element>
  </xsl:if>
</xsl:template>

<xsl:template match="*|@*">
  <xsl:param name="tag"/>
  <xsl:choose>
    <xsl:when test="$tag"><xsl:element name="{$tag}"><xsl:value-of select="."/></xsl:element></xsl:when>
    <xsl:otherwise>OOPS: <xsl:value-of select="name(.)"/></xsl:otherwise>
  </xsl:choose>
</xsl:template>
  <xsl:template match="fileDate|date|abDate|amendRegDate|autoProtDate|cancelDate|fileDate|firstUseDate|firstComUseDate|intDeathDate|intPubDate|intRegDate|intRenDate|intStatusDate|irrReplyByDate|locDate|notDate|origFileDateUS|priClaimedDate|pubOppDate|regDate|regExpDate|regRenDate|renDate|repub12cDate|statusDate|tranDate">
    <xsl:param name="tag"/>
    <xsl:choose>
      <xsl:when test="$tag and string-length($tag) &gt; 0"><xsl:element name="{$tag}"><xsl:call-template name="formatDate"><xsl:with-param name="date" select="."/></xsl:call-template></xsl:element></xsl:when>
      <xsl:otherwise>OOPS: <xsl:value-of select="name(.)"/></xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="desSearch">
      <xsl:for-each select="code">
	<xsl:variable name="class"><xsl:call-template name="splitClass"><xsl:with-param name="class" select="."/></xsl:call-template></xsl:variable>
        <xsl:element name="USC"><xsl:value-of select="$class"/></xsl:element>
	<xsl:if test="string-length($class) &gt; 4"><xsl:element name="VC2"><xsl:value-of select="substring($class, 1, 5)"/></xsl:element></xsl:if>
      </xsl:for-each>
  </xsl:template>

  <xsl:template match="statusCode">
    <xsl:element name="STATUS"><xsl:call-template name="getTagDescription"><xsl:with-param name="textType" select="'statusCode'"/><xsl:with-param name="tagName">status<xsl:value-of select="."/></xsl:with-param></xsl:call-template></xsl:element>

  </xsl:template>

  <xsl:template match="intCode">
    <!-- nice class, but it can have some garbage in it -->
    <xsl:variable name="myIntCode">
      <xsl:call-template name="trim">
	<xsl:with-param name="content" select="."/>
      </xsl:call-template>
    </xsl:variable>
      <xsl:choose>
	<xsl:when test="substring($myIntCode, 1, 1) = '0'">
	  <xsl:element name="NC">
	    <xsl:value-of select="substring($myIntCode, 2, 2)"/>
	  </xsl:element>
	</xsl:when>
	<xsl:when test="substring($myIntCode, 1, 1) = 'A'">
	  <xsl:element name="NC">01</xsl:element>
	  <xsl:element name="NC">02</xsl:element>
	  <xsl:element name="NC">03</xsl:element>
	  <xsl:element name="NC">04</xsl:element>
	  <xsl:element name="NC">05</xsl:element>
	  <xsl:element name="NC">06</xsl:element>
	  <xsl:element name="NC">07</xsl:element>
	  <xsl:element name="NC">08</xsl:element>
	  <xsl:element name="NC">09</xsl:element>
	  <xsl:element name="NC">10</xsl:element>
	  <xsl:element name="NC">11</xsl:element>
	  <xsl:element name="NC">12</xsl:element>
	  <xsl:element name="NC">13</xsl:element>
	  <xsl:element name="NC">14</xsl:element>
	  <xsl:element name="NC">15</xsl:element>
	  <xsl:element name="NC">16</xsl:element>
	  <xsl:element name="NC">17</xsl:element>
	  <xsl:element name="NC">18</xsl:element>
	  <xsl:element name="NC">19</xsl:element>
	  <xsl:element name="NC">20</xsl:element>
	  <xsl:element name="NC">21</xsl:element>
	  <xsl:element name="NC">22</xsl:element>
	  <xsl:element name="NC">23</xsl:element>
	  <xsl:element name="NC">24</xsl:element>
	  <xsl:element name="NC">25</xsl:element>
	  <xsl:element name="NC">26</xsl:element>
	  <xsl:element name="NC">27</xsl:element>
	  <xsl:element name="NC">28</xsl:element>
	  <xsl:element name="NC">29</xsl:element>
	  <xsl:element name="NC">30</xsl:element>
	  <xsl:element name="NC">31</xsl:element>
	  <xsl:element name="NC">32</xsl:element>
	  <xsl:element name="NC">33</xsl:element>
	  <xsl:element name="NC">34</xsl:element>
	</xsl:when>
	<xsl:when test="substring($myIntCode, 1, 1) = 'B'">
	  <xsl:element name="NC">35</xsl:element>
	  <xsl:element name="NC">36</xsl:element>
	  <xsl:element name="NC">37</xsl:element>
	  <xsl:element name="NC">38</xsl:element>
	  <xsl:element name="NC">39</xsl:element>
	  <xsl:element name="NC">40</xsl:element>
	  <xsl:element name="NC">41</xsl:element>
	  <xsl:element name="NC">42</xsl:element>
	  <xsl:element name="NC">43</xsl:element>
	  <xsl:element name="NC">44</xsl:element>
	  <xsl:element name="NC">45</xsl:element>
	</xsl:when>
	<xsl:otherwise>
	  <xsl:element name="NC">01</xsl:element>
	  <xsl:element name="NC">02</xsl:element>
	  <xsl:element name="NC">03</xsl:element>
	  <xsl:element name="NC">04</xsl:element>
	  <xsl:element name="NC">05</xsl:element>
	  <xsl:element name="NC">06</xsl:element>
	  <xsl:element name="NC">07</xsl:element>
	  <xsl:element name="NC">08</xsl:element>
	  <xsl:element name="NC">09</xsl:element>
	  <xsl:element name="NC">10</xsl:element>
	  <xsl:element name="NC">11</xsl:element>
	  <xsl:element name="NC">12</xsl:element>
	  <xsl:element name="NC">13</xsl:element>
	  <xsl:element name="NC">14</xsl:element>
	  <xsl:element name="NC">15</xsl:element>
	  <xsl:element name="NC">16</xsl:element>
	  <xsl:element name="NC">17</xsl:element>
	  <xsl:element name="NC">18</xsl:element>
	  <xsl:element name="NC">19</xsl:element>
	  <xsl:element name="NC">20</xsl:element>
	  <xsl:element name="NC">21</xsl:element>
	  <xsl:element name="NC">22</xsl:element>
	  <xsl:element name="NC">23</xsl:element>
	  <xsl:element name="NC">24</xsl:element>
	  <xsl:element name="NC">25</xsl:element>
	  <xsl:element name="NC">26</xsl:element>
	  <xsl:element name="NC">27</xsl:element>
	  <xsl:element name="NC">28</xsl:element>
	  <xsl:element name="NC">29</xsl:element>
	  <xsl:element name="NC">30</xsl:element>
	  <xsl:element name="NC">31</xsl:element>
	  <xsl:element name="NC">32</xsl:element>
	  <xsl:element name="NC">33</xsl:element>
	  <xsl:element name="NC">34</xsl:element>
	  <xsl:element name="NC">35</xsl:element>
	  <xsl:element name="NC">36</xsl:element>
	  <xsl:element name="NC">37</xsl:element>
	  <xsl:element name="NC">38</xsl:element>
	  <xsl:element name="NC">39</xsl:element>
	  <xsl:element name="NC">40</xsl:element>
	  <xsl:element name="NC">41</xsl:element>
	  <xsl:element name="NC">42</xsl:element>
	  <xsl:element name="NC">43</xsl:element>
	  <xsl:element name="NC">44</xsl:element>
	  <xsl:element name="NC">45</xsl:element>
	</xsl:otherwise>
      </xsl:choose>
  </xsl:template>

  <xsl:template match="usCode">
    <!-- us national code -->
    <xsl:variable name="myCode">
      <xsl:call-template name="trim">
	<xsl:with-param name="content" select="."/>
      </xsl:call-template>
    </xsl:variable>
    <xsl:element name="NGC">
      <xsl:choose>
	<xsl:when test="substring($myCode, 1, 2) = '00'"><xsl:value-of select="substring($myCode, 3, 1)"/></xsl:when>
	<xsl:when test="substring($myCode, 1, 1) = '0'"><xsl:value-of select="substring($myCode, 2, 2)"/></xsl:when>
	<xsl:otherwise><xsl:value-of select="$myCode"/></xsl:otherwise>
      </xsl:choose>
    </xsl:element>
  </xsl:template>

  <xsl:template match="mark">
    <xsl:if test="(string-length(.) &gt; 0) and not(. = ' ')">
      <xsl:element name="BRAND">
	<xsl:value-of select="."/>
      </xsl:element>
    </xsl:if>
  </xsl:template>

  <xsl:template match="stmt">
    <!-- what the tag is depend on what the type code is.  The dataimporthandler needs this to know what field to put things in -->

<!-- goods and services sometimes denotes 'less goods' in the type-code.  Should we ignore those words when searching? -->
    <xsl:variable name="tagName"><xsl:value-of select="substring(typeCode, 1, 2)"/>Stmt</xsl:variable>
    <xsl:element name="{$tagName}">
      <xsl:apply-templates select="text"/>
    </xsl:element>
  </xsl:template>

  <xsl:template match="owners">
      <xsl:for-each select="owner">
	<!-- only index the party name if it's different than the previous one -->
	<xsl:variable name="previous" select="preceding-sibling::*[1]/partyName"/>

	<xsl:if test="(position() = 1) or (not(partyName = $previous))"><xsl:apply-templates select="."/></xsl:if>
      </xsl:for-each>
  </xsl:template>

  <xsl:template match="owner">
    <xsl:apply-templates select="partyName"><xsl:with-param name="tag" select="'HOL_EN'"/></xsl:apply-templates>
    <xsl:apply-templates select="partyName"><xsl:with-param name="tag" select="'HOL_STR'"/></xsl:apply-templates>
    <xsl:apply-templates select="nat"/>
  </xsl:template>

  <xsl:template match="nat">
      <xsl:choose>
	<xsl:when test="not(country)">
	  <xsl:element name="HOLC">US</xsl:element>
	  <!-- <xsl:element name="NRH">0</xsl:element> -->
	</xsl:when>
	<xsl:otherwise>
	  <xsl:apply-templates select="country"><xsl:with-param name="tag" select="'HOLC'"/></xsl:apply-templates>
	  <!-- <xsl:element name="NRH"> -->
	  <!--   <xsl:choose> -->
	  <!--     <xsl:when test="country != 'US'">1</xsl:when> -->
	  <!--     <xsl:otherwise>0</xsl:otherwise> -->
	  <!--   </xsl:choose> -->
	  <!-- </xsl:element> -->
	</xsl:otherwise>
      </xsl:choose>
  </xsl:template>

  <xsl:template name="splitClass">
    <xsl:param name="class"/>
	<xsl:value-of select="substring($class, 1, 2)"/>
	<xsl:if test="string-length($class) &gt; 2">.<xsl:call-template name="splitClass"><xsl:with-param name="class" select="substring($class, 3)"/></xsl:call-template>
	</xsl:if>
  </xsl:template>

<xsl:template name="trim">
	<xsl:param name="content"/>
	<xsl:call-template name="trim-right">
	<xsl:with-param name="content">
		<xsl:call-template name="trim-left">
		<xsl:with-param name="content" select="$content"/>
		</xsl:call-template>
	</xsl:with-param>
	</xsl:call-template>
</xsl:template>

<xsl:template name="trim-left">
	<xsl:param name="content"/>
	<xsl:choose>
	<xsl:when test="starts-with($content, '	') or starts-with($content, '
') or starts-with($content, ' ') or starts-with($content, '
')">
		<xsl:call-template name="trim-left">
			<xsl:with-param name="content" select="substring($content, 2)"/>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:value-of select="$content"/>
	</xsl:otherwise>
	</xsl:choose>
</xsl:template>

<xsl:template name="trim-right">
	<xsl:param name="content"/>
	<xsl:variable name="length" select="string-length($content)"/>
	<xsl:variable name="last" select="substring($content, $length, 1)"/>
	<xsl:choose>
	<xsl:when test="($last = '	') or ($last = '
') or ($last = ' ') or ($last = '
')">
		<xsl:call-template name="trim-right">
		<xsl:with-param name="content" select="substring($content, 1, $length - 1)"/>
		</xsl:call-template>
	</xsl:when>
	<xsl:otherwise>
		<xsl:value-of select="$content"/>
	</xsl:otherwise>
	</xsl:choose>
</xsl:template>

  <xsl:template match="regNum">
    <xsl:element name="IRN"><xsl:value-of select="."/></xsl:element>
    <xsl:element name="RNS"><xsl:value-of select="."/></xsl:element>
  </xsl:template>

  <xsl:template match="serNum">
    <xsl:element name="AN"><xsl:value-of select="."/></xsl:element>
    <xsl:element name="ANS"><xsl:value-of select="."/></xsl:element>
    <xsl:element name="st13"><xsl:value-of select="$CC"/>50<xsl:call-template name="zeroPad"><xsl:with-param name="number" select="."/><xsl:with-param name="length" select="'9'"/></xsl:call-template></xsl:element>
  </xsl:template>

  <xsl:template name="zeroPad">
	  <xsl:param name="number"/>
          <xsl:param name="length"/>
	  <xsl:value-of select="substring('000000000', 1, $length - string-length($number))"/><xsl:value-of select="$number"/>
  </xsl:template>

  <xsl:template name="formatDate">
    <xsl:param name="date"/>
    <xsl:variable name="cleanDate"><xsl:value-of select="translate(., '.-/', '')"/></xsl:variable>
    <xsl:value-of select="substring($cleanDate, 0, 5)"/>-<xsl:value-of select="substring($cleanDate, 5, 2)"/>-<xsl:value-of select="substring($cleanDate, 7, 2)"/>T23:59:59Z</xsl:template>

</xsl:stylesheet>
