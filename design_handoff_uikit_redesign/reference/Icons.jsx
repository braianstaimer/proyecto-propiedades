// ui_kits/web/Icons.jsx — every glyph copied straight from frontend/src/components/*.vue
// All icons: 24x24 viewBox, stroke=currentColor, round caps/joins, aria-hidden by default.

const Icon = ({ d, size = 20, strokeWidth = 2, multi = null, ...rest }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
    {...rest}
  >
    {multi ?? <path d={d} />}
  </svg>
);

const HouseIcon = (p) => (
  <Icon {...p} multi={<><path d="M3 12 12 3l9 9" /><path d="M5 10v10h14V10" /><path d="M10 20v-5h4v5" /></>} />
);
const ApartmentIcon = (p) => (
  <Icon {...p} multi={<><path d="M3 21V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14" /><path d="M9 21V11" /><path d="M15 21V11" /></>} />
);
const TerrenoIcon = (p) => (
  <Icon {...p} multi={<><path d="M3 12h18" /><path d="M3 18h18" /><path d="M3 6h18" /></>} />
);
const OficinaIcon = (p) => (
  <Icon {...p} multi={<><path d="M6 4h12v16H6z" /><path d="M10 8h4" /><path d="M10 12h4" /><path d="M10 16h4" /></>} />
);
const LocalIcon = (p) => (
  <Icon {...p} multi={<><path d="M3 9 5 4h14l2 5" /><path d="M3 9v11h18V9" /><path d="M9 14h6" /></>} />
);
const SearchIcon = (p) => (
  <Icon {...p} multi={<><circle cx="11" cy="11" r="7" /><line x1="21" y1="21" x2="16.65" y2="16.65" /></>} />
);
const SpinnerIcon = (p) => (
  <Icon {...p} multi={<><circle cx="12" cy="12" r="10" strokeOpacity=".25" /><path d="M22 12a10 10 0 0 1-10 10" /></>} />
);
const ChevronsIcon = (p) => (
  <Icon {...p} multi={<><polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" /></>} />
);
const AlertCircleIcon = (p) => (
  <Icon {...p} multi={<><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></>} />
);
const XIcon = (p) => (
  <Icon {...p} multi={<><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></>} />
);
const MapPinIcon = (p) => (
  <Icon {...p} multi={<><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" /><circle cx="12" cy="10" r="3" /></>} />
);

const TIPO_ICONS = {
  casa: HouseIcon,
  departamento: ApartmentIcon,
  terreno: TerrenoIcon,
  oficina: OficinaIcon,
  local: LocalIcon,
};

const TIPO_GRADIENTS = {
  casa: 'linear-gradient(135deg, #e0eefe, #7fbffb)',
  departamento: 'linear-gradient(135deg, #fae6da, #eda181)',
  terreno: 'linear-gradient(135deg, #d1fae5, #6ee7b7)',
  oficina: 'linear-gradient(135deg, #ede9fe, #c4b5fd)',
  local: 'linear-gradient(135deg, #fef3c7, #fcd34d)',
};

const TagIcon = (p) => (
  <Icon {...p} multi={<><path d="M20.59 13.41 13.42 20.58a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" /><line x1="7" y1="7" x2="7.01" y2="7" /></>} />
);
const ArrowsLeftRightIcon = (p) => (
  <Icon {...p} multi={<><path d="m16 3 4 4-4 4" /><path d="M20 7H4" /><path d="m8 21-4-4 4-4" /><path d="M4 17h16" /></>} />
);
const SlidersIcon = (p) => (
  <Icon {...p} multi={<><line x1="4" y1="21" x2="4" y2="14" /><line x1="4" y1="10" x2="4" y2="3" /><line x1="12" y1="21" x2="12" y2="12" /><line x1="12" y1="8" x2="12" y2="3" /><line x1="20" y1="21" x2="20" y2="16" /><line x1="20" y1="12" x2="20" y2="3" /><line x1="1" y1="14" x2="7" y2="14" /><line x1="9" y1="8" x2="15" y2="8" /><line x1="17" y1="16" x2="23" y2="16" /></>} />
);
const CalendarIcon = (p) => (
  <Icon {...p} multi={<><rect x="3" y="4" width="18" height="18" rx="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" /></>} />
);
const SparklesIcon = (p) => (
  <Icon {...p} multi={<><path d="M12 3v3 M12 18v3 M3 12h3 M18 12h3 M5.6 5.6 7.7 7.7 M16.3 16.3 18.4 18.4 M5.6 18.4 7.7 16.3 M16.3 7.7 18.4 5.6" /></>} />
);

Object.assign(window, {
  Icon,
  HouseIcon, ApartmentIcon, TerrenoIcon, OficinaIcon, LocalIcon,
  SearchIcon, SpinnerIcon, ChevronsIcon, AlertCircleIcon, XIcon, MapPinIcon,
  TagIcon, ArrowsLeftRightIcon, SlidersIcon, CalendarIcon, SparklesIcon,
  TIPO_ICONS, TIPO_GRADIENTS,
});
