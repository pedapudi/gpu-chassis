# Drawing coverage

The manufacturing package has two drawing books: one for the full chassis and one for the upper module. Each includes all three fan options. Shared parts are drawn once instead of repeated for every configuration.

Each book groups related information into assembly and service access, rear interfaces and PCB seating, the printed adapter and metric hardware, fan carriers and the stock mesh cover, and compact part-detail sheets. Complete face contours and small formed views accompany dimensions, hole-family leaders and notes. Technical tables do not occupy standalone sheets.

The CSV feature schedules contain exact circular-feature centres and diameters. Nominal part STEP geometry defines the complete formed contours, including slots, reliefs and bends. The books summarize those details for human review; the STEP files and CSVs supply data for CAD inspection. Production flat patterns must use the selected fabricator's material thickness, bend tooling and tolerances.

Every manufactured chassis component has an individual STEP file and an entry in its configuration's parts index. Hardware is counted separately. Printed adapters also have print-bed-oriented STL files. Component fit references are excluded from STEP exports.

Drawing validation includes rendered-page inspection, text-boundary checks and geometry coverage. CAD validation includes solid validity, individual STEP round trips, changed-part interference and top-down access to the printed-adapter screws. Reports state the checks performed; they do not certify supplier fit, thermal performance or load capacity.
