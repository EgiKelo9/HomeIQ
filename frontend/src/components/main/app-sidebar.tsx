'use client'

import * as React from "react"
import Image from "next/image"
import { NavMain } from "@/components/main/nav-main"
import { Skeleton } from "../ui/skeleton"
import { ChartPie, ChartLine, Brain, DatabaseSearch } from "lucide-react"
import { Sidebar, SidebarContent, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem, SidebarRail } from "@/components/ui/sidebar"

const navMain = [
  {
    title: "Overview",
    url: "/overview",
    icon: ChartPie,
  },
  {
    title: "Analytics",
    url: "/analytics",
    icon: ChartLine,
  },
  {
    title: "Model",
    url: "/model",
    icon: Brain,
  },
  {
    title: "Scraper",
    url: "/scraper",
    icon: DatabaseSearch,
  },
]

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg">
              <div className="flex aspect-square size-8 items-center justify-center rounded-lg">
                <Image src="/vercel.jpg" alt="Logo" width={12} height={12} className="size-6 rounded-full" />
              </div>
              <span className="truncate font-bold leading-tight text-foreground text-lg">HomeIQ</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={navMain} />
      </SidebarContent>
      <SidebarRail />
    </Sidebar>
  )
}

export function AppSidebarSkeleton() {
  return (
    <div data-slot="sidebar" className="bg-sidebar text-sidebar-foreground hidden md:flex h-full min-h-screen w-(--sidebar-width) flex-col">
      <Skeleton className="w-full h-full rounded-lg m-4" />
    </div>
  )
}

export function AppUserSidebar() {
  return <AppSidebar />
}