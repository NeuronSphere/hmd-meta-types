package metatypes

import (
	"errors"
	"fmt"
	"strings"
	"time"
)

// Timestamp is a Python datetime: microsecond precision, either naive (no time
// zone) or aware. meta-types stores an aware value with a non-zero offset in UTC.
type Timestamp struct {
	t     time.Time
	aware bool
}

// NewTimestamp is an aware timestamp. Like Python, precision stops at microseconds.
func NewTimestamp(t time.Time) Timestamp {
	return Timestamp{t: t.Truncate(time.Microsecond), aware: true}
}

// NaiveTimestamp is a timestamp without a time zone; only t's wall clock is kept.
func NaiveTimestamp(t time.Time) Timestamp {
	y, mo, d := t.Date()
	h, mi, s := t.Clock()
	return Timestamp{t: time.Date(y, mo, d, h, mi, s, t.Nanosecond()/1000*1000, time.UTC)}
}

// Time is the timestamp as a time.Time. A naive timestamp is returned in UTC.
func (ts Timestamp) Time() time.Time { return ts.t }

// IsNaive reports whether the timestamp has no time zone.
func (ts Timestamp) IsNaive() bool { return !ts.aware }

// normalized is what meta-types' setter stores: aware values with a non-zero
// offset are converted to UTC.
func (ts Timestamp) normalized() Timestamp {
	if ts.aware {
		if _, off := ts.t.Zone(); off != 0 {
			ts.t = ts.t.UTC()
		}
	}
	return ts
}

// ISOFormat is Python's datetime.isoformat().
func (ts Timestamp) ISOFormat() string {
	t := ts.t
	s := fmt.Sprintf("%04d-%02d-%02dT%02d:%02d:%02d", t.Year(), int(t.Month()), t.Day(), t.Hour(), t.Minute(), t.Second())
	if us := t.Nanosecond() / 1000; us != 0 {
		s += fmt.Sprintf(".%06d", us)
	}
	if ts.aware {
		_, off := t.Zone()
		sign := "+"
		if off < 0 {
			sign, off = "-", -off
		}
		s += fmt.Sprintf("%s%02d:%02d", sign, off/3600, off/60%60)
		if off%60 != 0 {
			s += fmt.Sprintf(":%02d", off%60)
		}
	}
	return s
}

func (ts Timestamp) equal(o Timestamp) bool {
	if ts.aware != o.aware {
		return false // Python: naive and aware datetimes are never equal
	}
	return ts.t.Equal(o.t)
}

func (ts Timestamp) valid() bool {
	y := ts.t.Year()
	return y >= 1 && y <= 9999
}

var errISO = errors.New("invalid ISO-8601 timestamp")

// ParseISO is dateutil.parser.isoparse (dateutil 2.8.2), which meta-types uses to
// deserialize timestamps: common dates (YYYY, YYYY-MM, YYYY-MM-DD, YYYYMMDD),
// ISO week and ordinal dates, any single separator character, times with or
// without colons, fractions truncated to microseconds, hour 24, and Z or ±HH[:MM]
// offsets (a zero offset is UTC).
func ParseISO(s string) (Timestamp, error) {
	for i := 0; i < len(s); i++ {
		if s[i] >= 0x80 {
			return Timestamp{}, errISO // isoparse takes ASCII only
		}
	}
	date, pos, err := parseISODate(s)
	if err != nil {
		return Timestamp{}, err
	}
	var tc timeComponents
	if len(s) > pos {
		// Any single character separates date and time (isoparse's sep=None).
		tc, err = parseISOTime(s[pos+1:])
		if err != nil {
			return Timestamp{}, err
		}
	}
	addDay := false
	if tc.hour == 24 {
		tc.hour = 0
		addDay = true
	}
	if tc.hour > 23 || tc.minute > 59 || tc.second > 59 {
		return Timestamp{}, errISO
	}
	loc := time.UTC
	if tc.hasTZ && tc.offset != 0 {
		loc = time.FixedZone("", tc.offset)
	}
	t := time.Date(date[0], time.Month(date[1]), date[2], tc.hour, tc.minute, tc.second, tc.micro*1000, loc)
	if addDay {
		t = t.AddDate(0, 0, 1)
	}
	return Timestamp{t: t, aware: tc.hasTZ}, nil
}

func atoiDigits(s string) (int, bool) {
	if s == "" {
		return 0, false
	}
	n := 0
	for i := 0; i < len(s); i++ {
		if s[i] < '0' || s[i] > '9' {
			return 0, false
		}
		n = n*10 + int(s[i]-'0')
	}
	return n, true
}

func daysIn(year, month int) int {
	return time.Date(year, time.Month(month)+1, 0, 0, 0, 0, 0, time.UTC).Day()
}

func isLeap(year int) bool { return daysIn(year, 2) == 29 }

func parseISODate(s string) ([3]int, int, error) {
	d, pos, err := parseISODateCommon(s)
	if err != nil {
		d, pos, err = parseISODateUncommon(s)
	}
	if err != nil {
		return d, 0, err
	}
	if d[0] < 1 || d[0] > 9999 || d[1] < 1 || d[1] > 12 || d[2] < 1 || d[2] > daysIn(d[0], d[1]) {
		return d, 0, errISO
	}
	return d, pos, nil
}

func parseISODateCommon(s string) ([3]int, int, error) {
	c := [3]int{1, 1, 1}
	if len(s) < 4 {
		return c, 0, errISO
	}
	y, ok := atoiDigits(s[0:4])
	if !ok {
		return c, 0, errISO
	}
	c[0] = y
	pos := 4
	if pos >= len(s) {
		return c, pos, nil
	}
	hasSep := s[pos] == '-'
	if hasSep {
		pos++
	}
	if len(s)-pos < 2 {
		return c, 0, errISO
	}
	m, ok := atoiDigits(s[pos : pos+2])
	if !ok {
		return c, 0, errISO
	}
	c[1] = m
	pos += 2
	if pos >= len(s) {
		if hasSep {
			return c, pos, nil
		}
		return c, 0, errISO
	}
	if hasSep {
		if s[pos] != '-' {
			return c, 0, errISO
		}
		pos++
	}
	if len(s)-pos < 2 {
		return c, 0, errISO
	}
	d, ok := atoiDigits(s[pos : pos+2])
	if !ok {
		return c, 0, errISO
	}
	c[2] = d
	return c, pos + 2, nil
}

func parseISODateUncommon(s string) ([3]int, int, error) {
	var c [3]int
	if len(s) < 4 {
		return c, 0, errISO
	}
	year, ok := atoiDigits(s[0:4])
	if !ok || year < 1 {
		return c, 0, errISO
	}
	hasSep := len(s) > 4 && s[4] == '-'
	pos := 4
	if hasSep {
		pos++
	}
	var base time.Time
	if pos < len(s) && s[pos] == 'W' {
		pos++
		if pos+2 > len(s) {
			return c, 0, errISO
		}
		week, ok := atoiDigits(s[pos : pos+2])
		if !ok {
			return c, 0, errISO
		}
		pos += 2
		day := 1
		if len(s) > pos {
			if (s[pos] == '-') != hasSep {
				return c, 0, errISO
			}
			if hasSep {
				pos++
			}
			if pos >= len(s) {
				return c, 0, errISO
			}
			day, ok = atoiDigits(s[pos : pos+1])
			if !ok {
				return c, 0, errISO
			}
			pos++
		}
		if week < 1 || week > 53 || day < 1 || day > 7 {
			return c, 0, errISO
		}
		jan4 := time.Date(year, 1, 4, 0, 0, 0, 0, time.UTC)
		isoWeekday := int(jan4.Weekday())
		if isoWeekday == 0 {
			isoWeekday = 7
		}
		monday := jan4.AddDate(0, 0, -(isoWeekday - 1))
		base = monday.AddDate(0, 0, (week-1)*7+(day-1))
	} else {
		if len(s)-pos < 3 {
			return c, 0, errISO
		}
		ord, ok := atoiDigits(s[pos : pos+3])
		if !ok {
			return c, 0, errISO
		}
		pos += 3
		max := 365
		if isLeap(year) {
			max = 366
		}
		if ord < 1 || ord > max {
			return c, 0, errISO
		}
		base = time.Date(year, 1, 1, 0, 0, 0, 0, time.UTC).AddDate(0, 0, ord-1)
	}
	return [3]int{base.Year(), int(base.Month()), base.Day()}, pos, nil
}

type timeComponents struct {
	hour, minute, second, micro int
	hasTZ                       bool
	offset                      int // seconds east of UTC
}

func parseISOTime(s string) (timeComponents, error) {
	var tc timeComponents
	if len(s) < 2 {
		return tc, errISO
	}
	pos, comp := 0, -1
	hasSep := false
	vals := [4]int{}
	for pos < len(s) && comp < 5 {
		comp++
		if strings.ContainsRune("-+Zz", rune(s[pos])) {
			off, err := parseISOTZ(s[pos:])
			if err != nil {
				return tc, err
			}
			tc.hasTZ, tc.offset = true, off
			pos = len(s)
			break
		}
		if comp == 1 && s[pos] == ':' {
			hasSep = true
			pos++
		} else if comp == 2 && hasSep {
			if s[pos] != ':' {
				return tc, errISO
			}
			pos++
		}
		if comp < 3 {
			end := pos + 2
			if end > len(s) {
				end = len(s)
			}
			n, ok := atoiDigits(s[pos:end])
			if !ok {
				return tc, errISO
			}
			vals[comp] = n
			pos = end
		} else if comp == 3 {
			if pos >= len(s) || (s[pos] != '.' && s[pos] != ',') {
				continue
			}
			j := pos + 1
			for j < len(s) && s[j] >= '0' && s[j] <= '9' {
				j++
			}
			if j == pos+1 {
				continue
			}
			frac := s[pos+1 : j]
			if len(frac) > 6 {
				frac = frac[:6]
			}
			us, _ := atoiDigits(frac)
			for k := len(frac); k < 6; k++ {
				us *= 10
			}
			vals[3] = us
			pos = j
		}
	}
	if pos < len(s) {
		return tc, errISO
	}
	tc.hour, tc.minute, tc.second, tc.micro = vals[0], vals[1], vals[2], vals[3]
	if tc.hour == 24 && (tc.minute != 0 || tc.second != 0 || tc.micro != 0) {
		return tc, errISO
	}
	return tc, nil
}

func parseISOTZ(s string) (int, error) {
	if s == "Z" || s == "z" {
		return 0, nil
	}
	if len(s) != 3 && len(s) != 5 && len(s) != 6 {
		return 0, errISO
	}
	mult := 1
	switch s[0] {
	case '-':
		mult = -1
	case '+':
	default:
		return 0, errISO
	}
	hours, ok := atoiDigits(s[1:3])
	if !ok {
		return 0, errISO
	}
	minutes := 0
	if len(s) > 3 {
		start := 3
		if s[3] == ':' {
			start = 4
		}
		minutes, ok = atoiDigits(s[start:])
		if !ok {
			return 0, errISO
		}
	}
	if hours == 0 && minutes == 0 {
		return 0, nil
	}
	if minutes > 59 || hours > 23 {
		return 0, errISO
	}
	return mult * (hours*60 + minutes) * 60, nil
}
