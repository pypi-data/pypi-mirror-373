from datetime import datetime
from xml.etree.ElementTree import Element

import pytest

from .xml import XML
from .xml import XMLParseError


def test_xml():
    xml = XML.fromstring(
        """<?xml version="1.0" encoding="utf-8"?>
    <nsfoo:foobar xmlns="http://main" xmlns:nsfoo="http://foobar">
    <!-- 123123 -->
        xxx
        <nons>
        yyy</nons>
        <nons>
        yyy
        <nons1 a="b"/>
        zzz
        <nons2 a="b"/>    </nons>
        <main xmlns:ns3="http://asdf" ns3:tete="123"><ns3:tete


        >20211111141804</ns3:tete>
    <!-- 123123 -->
        yyy
            <ns3:tete>
            20211111141805
</ns3:tete></main>

zzz
</nsfoo:foobar>
    """,
        namespaces={
            "main": "{http://main}",
            "foobar": "{http://foobar}",
            "asdf": "{http://asdf}",
        },
    )
    expected_formatted = """<ns0:foobar xmlns:ns0="http://foobar" xmlns:ns1="http://main" xmlns:ns2="http://asdf">
  xxx
  <ns1:nons>yyy</ns1:nons>
  <ns1:nons>
    yyy
    <ns1:nons1 a="b" />
    zzz
    <ns1:nons2 a="b" />
  </ns1:nons>
  <ns1:main ns2:tete="123">
    <ns2:tete>20211111141804</ns2:tete>
    yyy
    <ns2:tete>20211111141805</ns2:tete>
  </ns1:main>
  zzz
</ns0:foobar>"""
    assert str(xml) == expected_formatted
    assert str(XML.fromstring(expected_formatted)) == expected_formatted

    foo = xml.find("{foobar}foobar")
    main = foo.find("{main}main")
    assert main.getattr("{asdf}tete", cast=int) == 123
    with pytest.raises(XMLParseError):
        main.getattr("{asdf}tete2", cast=int)
    with pytest.raises(XMLParseError):
        main.getattr("{asdf}tete2", cast=str)
    assert main.getattr("{asdf}tete2", cast=int, strict=False) is None
    assert main.getattr("{asdf}tete2", cast=str, strict=False) == ""
    with pytest.raises(XMLParseError):
        main.find("{asdf}tete2")
    assert main.find("{asdf}tete2", strict=False) is None
    assert main.findall("{main}main") == [main]
    assert main.findall("{main}tete2", strict=False) == []
    assert main.findtext("{asdf}tete") == "20211111141804"
    assert main.find("{asdf}tete").text == "20211111141804"
    assert main.text == ""
    assert main.tag == "{main}main"
    with pytest.raises(XMLParseError):
        assert main.findtext("{asdf}tete2")
    with pytest.raises(XMLParseError):
        assert main.findtext("{asdf}tete2", cast=str)
    assert main.findtext("{asdf}tete2", cast=str, strict=False) == ""
    tetes = main.findall("{asdf}tete")
    assert [tete.findtext() for tete in tetes] == ["20211111141804", "20211111141805"]
    assert [tete.findtext(cast=lambda val: datetime.strptime(val, "%Y%m%d%H%M%S")) for tete in tetes] == [  # noqa:DTZ007
        datetime(2021, 11, 11, 14, 18, 4),  # noqa: DTZ001
        datetime(2021, 11, 11, 14, 18, 5),  # noqa: DTZ001
    ]


def test_xml_junk():
    with pytest.raises(XMLParseError):
        XML.fromstring(">juuunnk")


def test_xml_empty_tag():
    xml = XML.fromstring(
        """<?xml version="1.0" encoding="utf-8"?>
            <nons><![CDATA[
        yyy
            ]]><nons>
        yyy
                <nons1 a="b"/>
        zzz
                <nons2 a="b"/>    </nons></nons>
    """
    )
    assert (
        repr(xml)
        == """<nons>
        yyy
            <nons>
        yyy
                <nons1 a="b" />
        zzz
                <nons2 a="b" />    </nons></nons>"""
    )
    assert (
        str(xml)
        == """<nons>
  yyy
  <nons>
    yyy
    <nons1 a="b" />
    zzz
    <nons2 a="b" />
  </nons>
</nons>"""
    )
    stuff = Element(None)
    stuff.text = "stuff"
    xml.element.append(stuff)
    expected_formatted = """<nons>
  yyy
  <nons>
    yyy
    <nons1 a="b" />
    zzz
    <nons2 a="b" />
  </nons>
  stuff
</nons>"""
    assert str(xml) == expected_formatted
    assert str(XML.fromstring(expected_formatted)) == expected_formatted


def test_xml_empty_text():
    xml = XML(Element("tete"))
    assert xml.findtext("tete", cast=str) == ""
    assert xml.findtext("tete", cast=str, strict=False) == ""
    with pytest.raises(XMLParseError):
        xml.findtext("tete", cast=int)


def test_xml_cast_fail():
    xml = XML.fromstring("<tete>x</tete>")
    assert xml.findtext("tete") == "x"
    with pytest.raises(XMLParseError):
        xml.findtext("tete", cast=int)

    xml = XML.fromstring('<tete foo="x"></tete>')
    assert xml.getattr("foo") == "x"
    with pytest.raises(XMLParseError):
        xml.getattr("foo", cast=int)


def test_soap_fault():
    data = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
<env:Header/>
<S:Body>
    <S:Fault xmlns="">
        <faultcode>S:Server</faultcode>
        <faultstring>-1</faultstring>
    </S:Fault>
</S:Body>
</S:Envelope>"""

    xml = XML.fromstring(data, namespaces={"S": "{http://schemas.xmlsoap.org/soap/envelope/}"})

    error = xml.find("{S}Body/{S}Fault")
    assert error.tag == "{S}Fault"
    assert error.text == ""
    assert error.findtext("faultcode") == "S:Server"
    assert error.findtext("faultstring") == "-1"


def test_soap_regular():
    data = """<?xml version='1.0' encoding='UTF-8'?>
<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/">
    <S:Header>
        <WorkContext xmlns="http://oracle.com/weblogic/soap/workarea/">
            123
        </WorkContext>
    </S:Header>
    <S:Body>
        <ns2:stuff xmlns:ns2="http://example.com/">
            <return>
                <foo>
                    <bar>1234</bar>
                </foo>
            </return>
        </ns2:stuff>
    </S:Body>
</S:Envelope>
"""
    xml = XML.fromstring(data, namespaces={"S": "{http://schemas.xmlsoap.org/soap/envelope/}"})

    assert {el.tag: el.text for el in xml.find(".//foo")} == {"bar": "1234"}
    assert {el.tag: el.text for el in xml.findall(".//foo")} == {"foo": ""}
