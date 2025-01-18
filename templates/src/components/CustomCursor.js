import React, { useEffect, useState } from 'react';

const CustomCursor = () => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const [isPointer, setIsPointer] = useState(false);

    useEffect(() => {
        const moveCursor = (e) => {
            setPosition({ x: e.clientX, y: e.clientY });
        };

        const checkPointer = () => {
            const target = document.elementFromPoint(position.x, position.y);
            setIsPointer(window.getComputedStyle(target).cursor === 'pointer');
        };

        window.addEventListener('mousemove', moveCursor);
        window.addEventListener('mouseover', checkPointer);

        return () => {
            window.removeEventListener('mousemove', moveCursor);
            window.removeEventListener('mouseover', checkPointer);
        };
    }, [position.x, position.y]);

    return (
        <>
            <div
                className="cursor-dot"
                style={{
                    left: `${position.x}px`,
                    top: `${position.y}px`,
                    transform: `scale(${isPointer ? 1.5 : 1})`
                }}
            />
            <div
                className="cursor-outline"
                style={{
                    left: `${position.x}px`,
                    top: `${position.y}px`,
                    transform: `scale(${isPointer ? 1.5 : 1})`
                }}
            />
        </>
    );
};

export default CustomCursor; 