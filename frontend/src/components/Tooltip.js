import * as RadixTooltip from "@radix-ui/react-tooltip";

const Tooltip = ({ children, text }) => {
  return (
    <RadixTooltip.Provider delayDuration={0}>
      <RadixTooltip.Root>
        <RadixTooltip.Trigger>{children}</RadixTooltip.Trigger>
        <RadixTooltip.Content className="tooltip" side={"top"} sideOffset={5}>
          {text}
          <RadixTooltip.Arrow className="tooltip-arrow" offset={10} height={6} width={6} />
        </RadixTooltip.Content>
      </RadixTooltip.Root>
    </RadixTooltip.Provider>
  );
};

export default Tooltip;
