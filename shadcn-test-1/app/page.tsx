import Image from "next/image";
import {
  Button,
} from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  ClockIcon,
  HelpCircleIcon,
  CircleIcon,
  XCircleIcon,
  CheckCircleIcon,
  ArrowRightIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  LayoutListIcon,
  MoreHorizontalIcon,
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";

const LOGO_SRC = "/41b3e41de2bd3801d96e4656419c385bb1b25a45.png";

const tasks = [
  {
    id: "TASK-5161",
    tag: "Documentation",
    title: "You can't compress the program without quantifying the open-source SS...",
    status: "In Progress",
    statusIcon: ClockIcon,
    priority: "Medium",
    priorityIcon: ArrowRightIcon,
  },
  {
    id: "TASK-1234",
    tag: "Documentation",
    title: "Try to calculate the EXE feed, maybe it will index the multi-byte pixel!",
    status: "Backlog",
    statusIcon: HelpCircleIcon,
    priority: "Medium",
    priorityIcon: ArrowRightIcon,
  },
  {
    id: "TASK-7181",
    tag: "Bug",
    title: "We need to bypass the neural TCP card!",
    status: "Todo",
    statusIcon: CircleIcon,
    priority: "High",
    priorityIcon: ArrowUpIcon,
  },
  {
    id: "TASK-2233",
    tag: "Feature",
    title: "The SAS interface is down, bypass the open-source pixel so we can back up the...",
    status: "Backlog",
    statusIcon: HelpCircleIcon,
    priority: "Medium",
    priorityIcon: ArrowRightIcon,
  },
  {
    id: "TASK-4455",
    tag: "Feature",
    title: "I'll parse the wireless SSL protocol, that should driver the API panel!...",
    status: "Canceled",
    statusIcon: XCircleIcon,
    priority: "Medium",
    priorityIcon: ArrowRightIcon,
  },
  {
    id: "TASK-9101",
    tag: "Bug",
    title: "Use the digital TLS panel, then you can transmit the haptic system!...",
    status: "Done",
    statusIcon: CheckCircleIcon,
    priority: "High",
    priorityIcon: ArrowUpIcon,
  },
  {
    id: "TASK-9202",
    tag: "Feature",
    title: "The UTF8 application is down, parse the neural bandwidth so we can back up th...",
    status: "Done",
    statusIcon: CheckCircleIcon,
    priority: "High",
    priorityIcon: ArrowUpIcon,
  },
  {
    id: "TASK-1121",
    tag: "Feature",
    title: "Generating the driver won't do anything, we need to quantify the 1080p SMTP b...",
    status: "In Progress",
    statusIcon: ClockIcon,
    priority: "Medium",
    priorityIcon: ArrowRightIcon,
  },
  {
    id: "TASK-3141",
    tag: "Feature",
    title: "We need to program the back-end THX pixel!",
    status: "Todo",
    statusIcon: CircleIcon,
    priority: "Low",
    priorityIcon: ArrowDownIcon,
  },
  {
    id: "TASK-5678",
    tag: "Documentation",
    title: "Calculating the bus won't do anything, we need to navigate the back-end...",
    status: "In Progress",
    statusIcon: ClockIcon,
    priority: "High",
    priorityIcon: ArrowUpIcon,
  },
];

export default function Page() {
  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Navbar — Figma spacing: 16px horizontal, 12px vertical, 8px gap */}
      <header className="border-b border-border px-(--figma-spacing-4) py-(--figma-spacing-3) flex items-center justify-end gap-(--figma-spacing-2)">
        <ThemeToggle />
        <Image
          src={LOGO_SRC}
          alt="Logo"
          width={40}
          height={40}
          className="rounded-full object-cover size-10"
        />
      </header>

      <main className="flex-1 p-(--figma-spacing-4) md:p-(--figma-spacing-8) max-w-5xl mx-auto w-full">
        {/* Welcome — Figma typography: 2xl (24/32), semibold; base/sm for subtitle */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-(--figma-spacing-4) mb-(--figma-spacing-8)">
          <div>
            <h1 className="text-(length:--figma-text-2xl-size) leading-(--figma-text-2xl-leading) tracking-(--figma-text-2xl-tracking) font-semibold">
              Welcome back!
            </h1>
            <p className="text-muted-foreground text-(length:--figma-text-sm-size) leading-(--figma-text-sm-leading) mt-(--figma-spacing-1)">
              Here&apos;s a list of your tasks for this month!
            </p>
          </div>
        </div>

        {/* Filters — Figma spacing: 8px gap, 16px margin-bottom */}
        <div className="flex flex-wrap items-center gap-(--figma-spacing-2) mb-(--figma-spacing-4)">
          <Input
            placeholder="Filter tasks..."
            className="max-w-xs"
          />
          <Button variant="outline">Status</Button>
          <Button variant="outline">Priority</Button>
          <Button variant="outline" className="ml-auto">
            <LayoutListIcon className="size-4" />
            View
          </Button>
        </div>

        {/* Task table */}
        <Card>
          <CardHeader className="sr-only">
            Task list
          </CardHeader>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full text-(length:--figma-text-sm-size) leading-(--figma-text-sm-leading)">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left p-(--figma-spacing-3) w-10">
                      <input type="checkbox" className="rounded border-input" aria-label="Select all" />
                    </th>
                    <th className="text-left p-(--figma-spacing-3) font-medium">Task</th>
                    <th className="text-left p-(--figma-spacing-3) font-medium">Title</th>
                    <th className="text-left p-(--figma-spacing-3) font-medium">Status</th>
                    <th className="text-left p-(--figma-spacing-3) font-medium">Priority</th>
                    <th className="text-right p-(--figma-spacing-3) w-10" />
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((task) => {
                    const StatusIcon = task.statusIcon;
                    const PriorityIcon = task.priorityIcon;
                    return (
                      <tr key={task.id} className="border-b border-border last:border-0 hover:bg-muted/50">
                        <td className="p-(--figma-spacing-3)">
                          <input type="checkbox" className="rounded border-input" aria-label={`Select ${task.id}`} />
                        </td>
                        <td className="p-(--figma-spacing-3) font-mono text-(length:--figma-text-xs-size) leading-(--figma-text-xs-leading)">{task.id}</td>
                        <td className="p-(--figma-spacing-3)">
                          <div className="flex flex-col gap-(--figma-spacing-1)">
                            <Badge variant="secondary" className="w-fit text-(length:--figma-text-xs-size)">
                              {task.tag}
                            </Badge>
                            <span className="text-muted-foreground line-clamp-1">{task.title}</span>
                          </div>
                        </td>
                        <td className="p-(--figma-spacing-3)">
                          <span className="inline-flex items-center gap-(--figma-spacing-1-5)">
                            <StatusIcon className="size-3.5 text-muted-foreground" />
                            {task.status}
                          </span>
                        </td>
                        <td className="p-(--figma-spacing-3)">
                          <span className="inline-flex items-center gap-(--figma-spacing-1-5)">
                            <PriorityIcon className="size-3.5 text-muted-foreground" />
                            {task.priority}
                          </span>
                        </td>
                        <td className="p-(--figma-spacing-3) text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon" aria-label="Actions">
                                <MoreHorizontalIcon className="size-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem>Edit</DropdownMenuItem>
                              <DropdownMenuItem variant="destructive">Delete</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Footer / Pagination — Figma spacing */}
        <footer className="flex flex-wrap items-center justify-between gap-(--figma-spacing-4) mt-(--figma-spacing-4) pt-(--figma-spacing-4) border-t border-border">
          <p className="text-muted-foreground text-(length:--figma-text-xs-size) leading-(--figma-text-xs-leading)">
            0 of 100 row(s) selected.
          </p>
          <div className="flex items-center gap-(--figma-spacing-4)">
            <div className="flex items-center gap-(--figma-spacing-2)">
              <span className="text-muted-foreground text-(length:--figma-text-xs-size) whitespace-nowrap">Rows per page</span>
              <Select defaultValue="10">
                <SelectTrigger className="w-16 h-7">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <span className="text-muted-foreground text-(length:--figma-text-xs-size) whitespace-nowrap">
              Page 1 of 10
            </span>
            <div className="flex items-center gap-0">
              <Button variant="outline" size="icon" aria-label="First page">&laquo;</Button>
              <Button variant="outline" size="icon" aria-label="Previous page">&lsaquo;</Button>
              <Button variant="outline" size="icon" aria-label="Next page">&rsaquo;</Button>
              <Button variant="outline" size="icon" aria-label="Last page">&raquo;</Button>
            </div>
          </div>
          <Image
            src={LOGO_SRC}
            alt="Logo"
            width={32}
            height={32}
            className="rounded-full object-cover size-8"
          />
        </footer>
      </main>
    </div>
  );
}
