package metatypes

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"
	"sync"
	"time"
)

// strptime directives, copied from CPython 3.11's _strptime.TimeRE (C locale).
var strptimeDirectives = map[byte]string{
	'd': `(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])`,
	'f': `(?P<f>[0-9]{1,6})`,
	'H': `(?P<H>2[0-3]|[0-1]\d|\d)`,
	'I': `(?P<I>1[0-2]|0[1-9]|[1-9])`,
	'j': `(?P<j>36[0-6]|3[0-5]\d|[1-2]\d\d|0[1-9]\d|00[1-9]|[1-9]\d|0[1-9]|[1-9])`,
	'm': `(?P<m>1[0-2]|0[1-9]|[1-9])`,
	'M': `(?P<M>[0-5]\d|\d)`,
	'S': `(?P<S>6[0-1]|[0-5]\d|\d)`,
	'y': `(?P<y>\d\d)`,
	'Y': `(?P<Y>\d\d\d\d)`,
	'z': `(?P<z>[+-]\d\d:?[0-5]\d(:?[0-5]\d(\.\d{1,6})?)?|(?-i:Z))`,
	'A': `(?P<A>monday|tuesday|wednesday|thursday|friday|saturday|sunday)`,
	'a': `(?P<a>mon|tue|wed|thu|fri|sat|sun)`,
	'B': `(?P<B>january|february|march|april|may|june|july|august|september|october|november|december)`,
	'b': `(?P<b>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)`,
	'p': `(?P<p>am|pm)`,
	'%': `%`,
}

var (
	monthsFull  = []string{"january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"}
	monthsAbbr  = []string{"jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"}
	strptimeRes sync.Map // format -> *regexp.Regexp or error
)

// errUnsupportedDirective marks a directive Python accepts but this port does not
// implement (week numbers, ISO years, locale composites, %Z). See
// HMD_META_TYPES_REQ_DIFF_002.
type errUnsupportedDirective struct{ directive byte }

func (e errUnsupportedDirective) Error() string {
	return fmt.Sprintf("strptime directive %%%c is not supported by the Go port", e.directive)
}

func strptimeRegexp(format string) (*regexp.Regexp, error) {
	if v, ok := strptimeRes.Load(format); ok {
		if err, isErr := v.(error); isErr {
			return nil, err
		}
		return v.(*regexp.Regexp), nil
	}
	re, err := compileStrptime(format)
	if err != nil {
		strptimeRes.Store(format, err)
		return nil, err
	}
	strptimeRes.Store(format, re)
	return re, nil
}

var (
	strptimeRegexChars = regexp.MustCompile(`([\\.^$*+?(){}\[\]|])`)
	strptimeSpace      = regexp.MustCompile(`\s+`)
)

func compileStrptime(format string) (*regexp.Regexp, error) {
	format = strptimeRegexChars.ReplaceAllString(format, `\$1`)
	format = strptimeSpace.ReplaceAllString(format, `\s+`)
	var b strings.Builder
	for {
		i := strings.IndexByte(format, '%')
		if i < 0 {
			b.WriteString(format)
			break
		}
		if i+1 >= len(format) {
			return nil, fmt.Errorf("stray %% in format")
		}
		b.WriteString(format[:i])
		d := format[i+1]
		re, ok := strptimeDirectives[d]
		if !ok {
			switch d {
			case 'U', 'W', 'w', 'u', 'G', 'V', 'c', 'x', 'X', 'Z':
				return nil, errUnsupportedDirective{d}
			}
			return nil, fmt.Errorf("'%c' is a bad directive in format", d)
		}
		b.WriteString(re)
		format = format[i+2:]
	}
	return regexp.Compile(`(?i)^(?:` + b.String() + `)`)
}

// strptime is datetime.strptime(value, format), returning only whether it
// succeeds; meta-types uses it to validate strings.
func strptime(value, format string) error {
	re, err := strptimeRegexp(format)
	if err != nil {
		return err
	}
	m := re.FindStringSubmatchIndex(value)
	if m == nil {
		return fmt.Errorf("time data %q does not match format %q", value, format)
	}
	if m[1] != len(value) {
		return fmt.Errorf("unconverted data remains: %s", value[m[1]:])
	}
	g := map[string]string{}
	for i, name := range re.SubexpNames() {
		if name != "" && m[2*i] >= 0 {
			g[name] = value[m[2*i]:m[2*i+1]]
		}
	}
	num := func(k string) (int, bool) {
		s, ok := g[k]
		if !ok {
			return 0, false
		}
		n, err := strconv.Atoi(strings.TrimSpace(s))
		return n, err == nil
	}

	year, hasYear := num("Y")
	if y, ok := num("y"); ok && !hasYear {
		if y <= 68 {
			year = y + 2000
		} else {
			year = y + 1900
		}
		hasYear = true
	}
	month, hasMonth := num("m")
	if s, ok := g["B"]; ok {
		month, hasMonth = indexOf(monthsFull, strings.ToLower(s))+1, true
	}
	if s, ok := g["b"]; ok {
		month, hasMonth = indexOf(monthsAbbr, strings.ToLower(s))+1, true
	}
	day, hasDay := num("d")
	if !hasMonth {
		month = 1
	}
	if !hasDay {
		day = 1
	}
	hour, _ := num("H")
	if h, ok := num("I"); ok {
		hour = h
		switch strings.ToLower(g["p"]) {
		case "am":
			if h == 12 {
				hour = 0
			}
		case "pm":
			if h != 12 {
				hour = h + 12
			}
		}
	}
	minute, _ := num("M")
	second, _ := num("S")

	if !hasYear {
		year = 1900 // CPython 3.11 has no leap-year fix, so a year-less Feb 29 fails
	}
	// A julian day, when given, overrides the month and day (CPython does the same).
	if julian, ok := num("j"); ok {
		t := time.Date(year, 1, 1, 0, 0, 0, 0, time.UTC).AddDate(0, 0, julian-1)
		year, month, day = t.Year(), int(t.Month()), t.Day()
	} else if month < 1 || month > 12 || day < 1 || day > daysIn(year, month) {
		return fmt.Errorf("day is out of range for month")
	}
	if year < 1 || year > 9999 || hour > 23 || minute > 59 || second > 59 {
		return fmt.Errorf("time component out of range")
	}
	if z, ok := g["z"]; ok && z != "Z" {
		if z[3] == ':' {
			z = z[:3] + z[4:]
			if len(z) > 5 {
				if z[5] != ':' {
					return fmt.Errorf("inconsistent use of : in %s", g["z"])
				}
				z = z[:5] + z[6:]
			}
		}
		h, _ := strconv.Atoi(z[1:3])
		mi, _ := strconv.Atoi(z[3:5])
		sec := 0
		if len(z) >= 7 {
			sec, _ = strconv.Atoi(z[5:7])
		}
		// timezone(timedelta(...)) must be strictly between -24h and 24h.
		if h*3600+mi*60+sec >= 24*3600 {
			return fmt.Errorf("offset must be a timedelta strictly between -24h and 24h")
		}
	}
	return nil
}

func indexOf(list []string, s string) int {
	for i, v := range list {
		if v == s {
			return i
		}
	}
	return -1
}
